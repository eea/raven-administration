import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import requests


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))


def is_job_enabled():
    """Check if the notifications cron job is enabled via environment variables"""
    enabled = os.environ.get('CRON_NOTIFICATIONS_ENABLED', 'false').lower()
    return enabled in ('true', '1', 'yes', 'on')


def get_min_interval_hours():
    """Get the minimum interval in hours for missing data detection"""
    try:
        return int(os.environ.get('CRON_NOTIFICATIONS_MIN_INTERVAL_HOURS', '3'))
    except ValueError:
        return 3  # Default to 3 hours if invalid


def get_mail_method():
    """Get the mail sending method: 'smtp' (default) or 'graph'"""
    return os.environ.get('MAIL_METHOD', 'smtp').lower()


def get_graph_access_token():
    """Acquire an app-only access token via the client credentials flow"""
    tenant_id = os.environ.get('GRAPH_TENANT_ID')
    client_id = os.environ.get('GRAPH_CLIENT_ID')
    client_secret = os.environ.get('GRAPH_CLIENT_SECRET')
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
    }
    resp = requests.post(url, data=data, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Token request failed {resp.status_code}: {resp.text}")
    return resp.json()['access_token']


def send_via_graph(access_token, sender, to_address, subject, body):
    """Send a plaintext email via Microsoft Graph as `sender`"""
    url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to_address}}],
        },
        "saveToSentItems": "false",
    }
    resp = requests.post(
        url, json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 202:
        raise Exception(f"Graph API error {resp.status_code}: {resp.text}")


def log_cycle_summary(curs, run_datetime, cycle_logger, smtp_server=None, execution_time_ms=None):
    """Log a single consolidated summary for the entire cycle to notifications_runs table"""
    try:
        send_failures = [event for event in cycle_logger.events if 'Failed to send email to' in event]
        error_message = None

        if cycle_logger.has_error:
            status = "ERROR"
            error_events = [event for event in cycle_logger.events if event.startswith('ERROR:')]
            error_message = '; '.join(error_events) if error_events else "Unknown error occurred"
        elif cycle_logger.emails_failed and not cycle_logger.emails_sent:
            # Nothing was delivered this cycle
            status = "ERROR"
            error_message = '; '.join(send_failures) or None
        elif cycle_logger.emails_failed or cycle_logger.has_partial_delivery:
            status = "PARTIAL_SUCCESS"
            error_message = '; '.join(send_failures) or None
        else:
            status = "SUCCESS"

        # Prepare details JSON
        details = {
            "notifications_processed": cycle_logger.notifications_processed,
            "notifications_skipped": cycle_logger.notifications_skipped,
            "events": cycle_logger.events
        }

        log_sql = """
            INSERT INTO public.notifications_runs 
            (run_timestamp, missing_data_count, notifications_sent, notifications_failed, 
             smtp_server, execution_time_ms, status, error_message, details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        curs.execute(log_sql, (
            run_datetime,
            cycle_logger.missing_data_count,
            cycle_logger.emails_sent,
            cycle_logger.emails_failed,
            smtp_server,
            execution_time_ms,
            status,
            error_message,
            json.dumps(details)
        ))

        summary = cycle_logger.get_summary()
        print(f"LOG: {summary}")
    except Exception as e:
        print(f"Failed to log cycle summary: {e}")


class CycleLogger:
    """Collects events during the cycle and creates a consolidated summary"""

    def __init__(self):
        self.events = []
        self.has_error = False
        self.has_partial_delivery = False
        self.missing_data_count = 0
        self.notifications_processed = 0
        self.emails_sent = 0
        self.emails_failed = 0
        self.notifications_skipped = 0
        self.smtp_server = None

    def add_event(self, message, is_error=False):
        self.events.append(f"{'ERROR: ' if is_error else ''}{message}")
        if is_error:
            self.has_error = True

    def set_missing_data(self, count):
        self.missing_data_count = count

    def set_smtp_server(self, server, port):
        self.smtp_server = f"{server}:{port}"

    def notification_processed(self):
        self.notifications_processed += 1

    def email_sent(self):
        self.emails_sent += 1

    def email_failed(self):
        self.emails_failed += 1

    def partial_delivery(self):
        self.has_partial_delivery = True

    def notification_skipped(self):
        self.notifications_skipped += 1

    def get_summary(self):
        if self.missing_data_count == 0:
            return "No missing data found - no action required"

        summary_parts = [
            f"Found {self.missing_data_count} sampling points with missing data",
            f"Processed {self.notifications_processed} notifications"
        ]

        if self.emails_sent > 0:
            summary_parts.append(f"Successfully sent {self.emails_sent} emails")

        if self.emails_failed > 0:
            summary_parts.append(f"Failed to send {self.emails_failed} emails")

        if self.notifications_skipped > 0:
            summary_parts.append(f"Skipped {self.notifications_skipped} notifications (no relevant data)")

        if self.has_error or self.emails_failed or self.has_partial_delivery:
            summary_parts.append("Completed with errors")
        else:
            summary_parts.append("Completed successfully")

        return " | ".join(summary_parts)


# Check if the job is enabled
if not is_job_enabled():
    print("Notifications cron job is disabled via CRON_NOTIFICATIONS_ENABLED environment variable. Exiting.")
    sys.exit(0)

try:
    conn = psycopg2.connect(os.environ.get('DB_URI'))
    conn.autocommit = True  # Enable autocommit for logging
except:
    print("I am unable to connect to the database")
    sys.exit(1)

run_start_time = datetime.now()
cycle_logger = CycleLogger()

with conn.cursor() as curs:

    try:
        # Get configurable interval
        min_interval_hours = get_min_interval_hours()

        # Find missing data
        sql_missing = f"""
          SELECT sp.id as spo,
                s.name as station, 
                p.notation as pollutant, 
                c.notation as concentration, 
                t.label as timestep, 
                to_char(sp.to_time,'yyyy-mm-dd HH24:mi') as totime
          FROM sampling_points sp, stations s, eea_pollutants p, eea_concentrations c, eea_times t
          WHERE sp.station_id = s.id
          AND sp.pollutant = p.uri
          AND sp.concentration = c.id
          AND sp.timestep = t.id
          AND to_time IS NOT NULL
          AND to_time < now() - interval '{min_interval_hours} hours'
        """
        curs.execute(sql_missing)
        missing_data = curs.fetchall()

        cycle_logger.set_missing_data(len(missing_data))

        if not missing_data:
            print("No missing data found. Exiting.")
            execution_time_ms = int((datetime.now() - run_start_time).total_seconds() * 1000)
            log_cycle_summary(curs, run_start_time, cycle_logger, None, execution_time_ms)
            sys.exit(0)

        # Send email if missing data found
        print(f"Found {curs.rowcount} sampling points with missing data (last update > {min_interval_hours} hours ago).")
        sql_emails = """ 
            SELECT 
              n.name,
              n.emails, 
              COALESCE(
                  array_agg(ns.sampling_point_id) FILTER(WHERE ns.sampling_point_id IS NOT NULL),
                  '{}'
              ) AS sampling_points
            FROM notifications n
            LEFT JOIN notifications_samplingpoints ns ON n.name = ns.notification_id
            WHERE n.enabled = true
            GROUP BY n.name, n.emails
            ORDER BY n.name
        """
        curs.execute(sql_emails)
        notifications = curs.fetchall()

        if not notifications:
            cycle_logger.add_event("No enabled notifications found")
            print("No enabled notifications found. Exiting.")
            execution_time_ms = int((datetime.now() - run_start_time).total_seconds() * 1000)
            log_cycle_summary(curs, run_start_time, cycle_logger, None, execution_time_ms)
            sys.exit(0)

        mail_method = get_mail_method()
        graph_token = None
        graph_sender = None
        if mail_method == 'graph':
            graph_sender = os.environ.get('GRAPH_SENDER')
            try:
                graph_token = get_graph_access_token()
                cycle_logger.smtp_server = f"graph:{graph_sender}"
            except Exception as e:
                cycle_logger.add_event(f"Failed to acquire Graph API access token: {e}", True)
                print(f"Failed to acquire Graph API access token: {e}")
                execution_time_ms = int((datetime.now() - run_start_time).total_seconds() * 1000)
                log_cycle_summary(curs, run_start_time, cycle_logger, cycle_logger.smtp_server, execution_time_ms)
                sys.exit(1)

        for note in notifications:
            email_list = note[1].split(';')
            # find sampling points relevant to this notification
            filtered_data = [row for row in missing_data if row[0] in note[2] or not note[2]]
            if not filtered_data:
                cycle_logger.notification_skipped()
                print(f"No missing data for notification '{note[0]}'. Skipping email.")
                continue

            # Process this notification
            cycle_logger.notification_processed()

            print(f"Sending email to {note[0]} ({', '.join(email_list)}) for {len(filtered_data)} sampling points.")

            # Construct email content (same for all recipients)
            subject = f"RAVEN Notification: {len(filtered_data)} Sampling Points with Missing Data"
            body = f"The following sampling points have missing data (last update > {min_interval_hours} hours ago):\n\n"
            body += "Sampling Point ID | Station | Pollutant | Concentration | Timestep | Last Update\n"
            body += "-" * 80 + "\n"
            for row in filtered_data:
                body += f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}\n"

            if mail_method != 'graph':
                # Get SMTP configuration
                smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
                smtp_port = int(os.environ.get('SMTP_PORT', '587'))
                smtp_user = os.environ.get('SMTP_USER')
                smtp_password = os.environ.get('SMTP_PASSWORD')

                # Log SMTP server info (only once per cycle)
                if cycle_logger.smtp_server is None:
                    cycle_logger.set_smtp_server(smtp_server, smtp_port)

                print(f"Connecting to SMTP server at {smtp_server}:{smtp_port}")

            # Send email individually to each recipient
            successful_emails = []
            failed_emails = []

            for email_address in email_list:
                email_address = email_address.strip()
                if not email_address:
                    continue

                try:
                    if mail_method == 'graph':
                        send_via_graph(graph_token, graph_sender, email_address, subject, body)
                    else:
                        # Create individual message for this recipient
                        msg = MIMEMultipart()
                        msg['From'] = os.environ.get('SMTP_FROM', 'raven@example.com')
                        msg['To'] = email_address
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body, 'plain'))

                        # Send to this individual recipient
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            if smtp_user and smtp_password:
                                server.starttls()  # Enable encryption
                                server.login(smtp_user, smtp_password)
                            server.send_message(msg)

                    successful_emails.append(email_address)
                    print(f"Email sent successfully to {email_address}")

                except Exception as e:
                    failed_emails.append(email_address)
                    cycle_logger.add_event(f"Failed to send email to {email_address}: {str(e)}", False)
                    print(f"Failed to send email to {email_address}: {e}")

            # Update cycle logger with results based on overall outcome
            if successful_emails and not failed_emails:
                # All emails sent successfully to SMTP server
                cycle_logger.email_sent()
                print(f"Email notification '{note[0]}' sent to SMTP server for all {len(successful_emails)} recipients: {', '.join(successful_emails)}")
            elif not successful_emails and failed_emails:
                # All emails failed at SMTP level
                cycle_logger.email_failed()
                print(f"Email notification '{note[0]}' failed at SMTP level for all {len(failed_emails)} recipients: {', '.join(failed_emails)}")
            elif successful_emails and failed_emails:
                # Mixed results - mark as partial delivery
                cycle_logger.email_sent()
                cycle_logger.partial_delivery()
                print(f"Email notification '{note[0]}' partial SMTP delivery: {len(successful_emails)} sent ({', '.join(successful_emails)}), {len(failed_emails)} failed ({', '.join(failed_emails)})")
            else:
                # No valid email addresses
                cycle_logger.add_event(f"No valid email addresses found for notification '{note[0]}'", False)
                print(f"No valid email addresses found for notification '{note[0]}'")        # Log consolidated summary for this cycle
        execution_time_ms = int((datetime.now() - run_start_time).total_seconds() * 1000)
        log_cycle_summary(curs, run_start_time, cycle_logger, cycle_logger.smtp_server, execution_time_ms)
        print("Done")

    except (Exception, psycopg2.DatabaseError) as error:
        cycle_logger.add_event(f"Script error: {str(error)}", True)
        execution_time_ms = int((datetime.now() - run_start_time).total_seconds() * 1000)
        log_cycle_summary(curs, run_start_time, cycle_logger, cycle_logger.smtp_server, execution_time_ms)
        print(error)
        sys.exit(1)


curs.close()
