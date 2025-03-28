```mermaid
graph TD
erDiagram
    converted_series {
        BIGINT id PK "PRIMARY KEY"
        VARCHAR sampling_point_id FK "FOREIGN KEY"
        VARCHAR source FK "FOREIGN KEY"
        VARCHAR target FK "FOREIGN KEY"
        NUMERIC factor
        VARCHAR createdby
    }

    sampling_points {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR media_monitored FK "FOREIGN KEY"
        VARCHAR station_id FK "FOREIGN KEY"
        VARCHAR measurement_regime FK "FOREIGN KEY"
        BOOLEAN mobile
        VARCHAR assessment_type FK "FOREIGN KEY"
        VARCHAR station_classification FK "FOREIGN KEY"
    }

    stations {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR name
        VARCHAR begin_position
        VARCHAR end_position
        VARCHAR network_id FK "FOREIGN KEY"
    }

    networks {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR name
        VARCHAR media_monitored FK "FOREIGN KEY"
        VARCHAR responsible_authority_id FK "FOREIGN KEY"
    }

    responsible_authorities {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR name
        VARCHAR organisation
    }

    observations {
        BIGSERIAL id PK "PRIMARY KEY"
        VARCHAR sampling_point_id FK "FOREIGN KEY"
        VARCHAR begin_position
        VARCHAR end_position
        NUMERIC value
        TIMESTAMP from_time
        TIMESTAMP to_time
        VARCHAR qc_status FK "FOREIGN KEY"
    }

    qc_status {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR status
        VARCHAR description
        TIMESTAMP qc_date
        VARCHAR qc_performed_by
    }

    eea_adjustmenttypes {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR uri
    }

    eea_areaclassifications {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR notation
    }

    eea_assessmentthresholdexceedances {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR uri
    }

    eea_assessmenttypes {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR notation
    }

    eea_concentrations {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR notation
    }

    eea_exceedancedescription {
        INTEGER id PK "PRIMARY KEY"
        VARCHAR name
    }

    eea_exceedancereason {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR label
        VARCHAR uri
    }

    eea_exceedancetype {
        NUMERIC id PK "PRIMARY KEY"
        VARCHAR name
    }

    exceedancedescriptions {
        VARCHAR id PK "PRIMARY KEY"
        VARCHAR attainment_id FK "FOREIGN KEY"
        BOOLEAN exceedances
        INTEGER exceedance_type FK "FOREIGN KEY"
        NUMERIC max_value
        VARCHAR adjustment_type FK "FOREIGN KEY"
        NUMERIC surface_area
        INTEGER exposed_population
        INTEGER population_reference_year
        VARCHAR area_classification FK "FOREIGN KEY"
        VARCHAR exceedance_reason FK "FOREIGN KEY"
        INTEGER exceedancedescription_element FK "FOREIGN KEY"
        VARCHAR qc_status FK "FOREIGN KEY"
    }

    converted_series ||--|{ sampling_points : "sampling_point_id"
    sampling_points ||--|{ stations : "station_id"
    stations ||--|{ networks : "network_id"
    networks ||--|{ responsible_authorities : "responsible_authority_id"
    observations ||--|{ sampling_points : "sampling_point_id"
    observations ||--|| qc_status : "qc_status"
    exceedancedescriptions ||--|{ eea_exceedancetype : "exceedance_type"
    exceedancedescriptions ||--|{ eea_adjustmenttypes : "adjustment_type"
    exceedancedescriptions ||--|{ eea_areaclassifications : "area_classification"
    exceedancedescriptions ||--|{ eea_exceedancereason : "exceedance_reason"
    exceedancedescriptions ||--|{ eea_exceedancedescription : "exceedancedescription_element"
    exceedancedescriptions ||--|| qc_status : "qc_status"
```