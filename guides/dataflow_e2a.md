# Dataflow E2a

Use this endpoint to create the xml E2a dataflow.  
This also allows EEA to retrieve data directly if needed

## Group & User

Before retrieving the data you need to create a user with the necessary rights.  
In the Raven web site create a new Group with `EEA dataflow` and `All networks` enabled.  
Next, create a User with the new Group.

## Token

To get the token make a call to the authentication endpoint with the new users credentials

```yaml
POST api/auth/signin
BODY {"username":"username", "password":"password"}
```

## E2a

Make a call to the E2a endpoint to get the xml.  
Remember to include the token received earlier.  
`last_request` is a datetime format that gives you all changes since your last request.  
It will typically be **_now() - 1 hours_**

```yaml
GET api/dataflow/e2a?last_request=<DATETIME>
Authorization: Bearer <MY_TOKEN>
```

## E2a without authentication

It is possible to get E2a data without using a token, but this require the installation of `raven-public-api` and setting the .env variable `INCLUDE_EEA = True`  
See https://git.nilu.no/raven/raven-public-api#eeae2a
