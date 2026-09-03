INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('A1', 'Volcanic eruption or volcanism inside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/A1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('A2', 'Volcanic eruption or volcanism outside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/A2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('B', 'Coastal wetlands. Applicable to SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/B');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('B1', 'Seismic activity inside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/B1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('B2', 'Seismic activity outside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/B2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('C1', 'Geothermal activity inside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/C1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('C2', 'Geothermal activity outside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/C2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('D1', 'Wild-land/natural fire inside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/D1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('D2', 'Wild-land/natural fire outside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/D2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('E1', 'High wind event inside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/E1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('E2', 'High wind event outside the Member State. Applicable to PM & SO2.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/E2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('F1', 'Atmospheric resuspension inside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/F1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('F2', 'Atmospheric resuspension outside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/F2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('G1', 'Transport of natural particles from dry regions inside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/G1');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('G2', 'Transport of natural particles from dry regions outside the Member State. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/G2');
INSERT INTO public.eea_adjustmentsourcetype (id, label, uri) VALUES ('H', 'Sea spray. Applicable to PM only.', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmentsourcetype/H');

INSERT INTO public.eea_adjustmenttypes (id, label, uri) VALUES ('fullyCorrected', 'Fully corrected', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmenttype/fullyCorrected');
INSERT INTO public.eea_adjustmenttypes (id, label, uri) VALUES ('noneApplicable', 'No corrections applicable', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmenttype/noneApplicable');
INSERT INTO public.eea_adjustmenttypes (id, label, uri) VALUES ('nsCorrection', 'Natural source correction', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmenttype/nsCorrection');
INSERT INTO public.eea_adjustmenttypes (id, label, uri) VALUES ('wssCorrection', 'Winter-sanding or -salting correction', 'http://dd.eionet.europa.eu/vocabulary/aq/adjustmenttype/wssCorrection');

INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('rural', 'Rural', 'Rural', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/rural');
INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('rural-nearcity', 'Rural-Near_city', 'Rural-Near_city', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/rural-nearcity');
INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('rural-regional', 'Rural-Regional', 'Rural-Regional', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/rural-regional');
INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('rural-remote', 'Rural-Remote', 'Rural-Remote', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/rural-remote');
INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('suburban', 'Suburban', 'Suburban', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/suburban');
INSERT INTO public.eea_areaclassifications (id, label, notation, uri) VALUES ('urban', 'Urban', 'Urban', 'http://dd.eionet.europa.eu/vocabulary/aq/areaclassification/urban');

INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('aboveLTO', 'Above the long-term objective', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/aboveLTO');
INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('aboveUAT', 'Above Upper Assessment Threshold (>UAT)', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/aboveUAT');
INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('belowLAT', 'Below Lower Assessment Threshold (<LAT)', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/belowLAT');
INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('belowLTO', 'Below the long-term objective', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/belowLTO');
INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('LAT-UAT', 'Between the upper and lower threshold (LAT-UAT), on 3 or more occasions during the 5 previous years.', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/LAT-UAT');
INSERT INTO public.eea_assessmentthresholdexceedances (id, label, uri) VALUES ('NA', 'Not Applicable', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmentthresholdexceedance/NA');

INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('fixed', 'Fixed measurement', 'Fixed measurement', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/fixed');
INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('fixedrandom', 'Fixed random measurements', 'Fixed random measurements', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/fixedrandom');
INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('model', 'Modelling', 'Modelling', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/model');
INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('indicative', 'Indicative measurement', 'Indicative measurement', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/indicative');
INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('other', 'Other measurement', 'Other measurement', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/other');
INSERT INTO public.eea_assessmenttypes (id, label, notation, uri) VALUES ('objective', 'Objective estimation', 'Objective estimation', 'http://dd.eionet.europa.eu/vocabulary/aq/assessmenttype/objective');

INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('m-1', 'Per meter', 'm-1', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/m-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mg.l-1', 'Micrograms per litre.', 'mg/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mg.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mg.m-3', 'Miligrams per cubic metre of ambient air', 'mg/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mg.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mg.m-3.day', 'Micrograms per cubic meter times day', 'mg/m-3.day', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mg.m-3.day');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mg.m-3.h', 'Micrograms per cubic meter times hour', 'mg/m3.h', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mg.m-3.h');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mgN.l-1', 'Milligrams nitrogen per litre', 'mg N/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mgN.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mgN.m-2.m-1', 'Milligrams nitrogen per square meter per month', 'mg N/m2/m', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mgN.m-2.m-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mgS.l-1', 'Milligrams sulphur per litre', 'mg S/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mgS.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mgS.m-1', 'Milligrams nitrogen per meter', 'mgS.m-1', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mgS.m-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mgS.m-2.m-1', 'Milligrams sulphur per square meter per month', 'mg S/m2.m', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mgS.m-2.m-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('mm', 'Millimeter', 'mm', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/mm');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ng.l-1', 'Nanograms per litre', 'ng/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ng.m-2', 'Nanograms per square meter', 'ng/m2', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.m-2');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ng.m-2.day-1', 'Nanograms per square metre per day', 'ng/m2/day', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.m-2.day-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ng.m-3', 'Nanograms per cubic metre of ambient air', 'ng/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ng.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('pHunits', 'pH', 'pH units', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/pHunits');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('pg.m-3', 'Picograms per cubic metre of ambient air', 'pg/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/pg.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ppbv', 'Parts per billion per volume', 'ppbv', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ppbv');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ppmv', 'Parts per million by volume', 'ppmv', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ppmv');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('pptv', 'Parts per trillion per volume', 'pptv', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/pptv');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('uS.cm-1', 'Micro Siemens per centimeter', 'uS/cm', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/uS.cm-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ueH.l-1', 'micromoles per litre', 'ue H/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ueH.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ug.m-2.day-1', 'Micrograms per square metre per day', 'ug/m2/day', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-2.day-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ug.m-3.day', 'Micrograms per cubic metre per day', 'ug/m3.day', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3.day');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ug.m-3.h', 'Micrograms per cubic metre per hour', 'ug/m3.h', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3.h');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ugNO2.m-3', 'Units of mass concentration of nitrogen dioxide (?g/m3)', 'ugNO2/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ugNO2.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('pg.m-2.day-1', 'Picograms per square metre per day', 'pg/m2/day', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/pg.m-2.day-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('fg.m-3', 'Femtograms per cubic metre of ambient air', 'fg/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/fg.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ugC.m-3', 'Micrograms of carbon per cubic metre', 'µg C/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ugC.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ug.l-1', 'Micrograms per litre', 'µg/l', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.l-1');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ugS.m-3', 'Micrograms of sulphur per cubic metre', 'µg S/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ugS.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ug.m-3', 'Micrograms per cubic meter', 'µg/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ug.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ugN.m-3', 'Micrograms of nitrogen per cubic metre', 'µg N/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ugN.m-3');
INSERT INTO public.eea_concentrations (id, label, notation, uri) VALUES ('ugSO2.m-3', 'Micrograms of sulphur dioxide per cubic metre', 'µg SO2/m3', 'http://dd.eionet.europa.eu/vocabulary/uom/concentration/ugSO2.m-3');

INSERT INTO public.eea_equivalencedemonstrated (id, label, notation, uri) VALUES ('inprogress', 'Equivalence testing in progress', 'Equivalence testing in progress', 'http://dd.eionet.europa.eu/vocabulary/aq/equivalencedemonstrated/inprogress');
INSERT INTO public.eea_equivalencedemonstrated (id, label, notation, uri) VALUES ('no', 'Equivalence not demonstrated', 'Equivalence not demonstrated', 'http://dd.eionet.europa.eu/vocabulary/aq/equivalencedemonstrated/no');
INSERT INTO public.eea_equivalencedemonstrated (id, label, notation, uri) VALUES ('noRef', 'Demonstration not possible, no reference method defined by Directive', 'Demonstration not possible, no reference method defined by Directive', 'http://dd.eionet.europa.eu/vocabulary/aq/equivalencedemonstrated/noRef');
INSERT INTO public.eea_equivalencedemonstrated (id, label, notation, uri) VALUES ('ref', 'Reference method used, demonstration not necessary', 'Reference method used, demonstration not necessary', 'http://dd.eionet.europa.eu/vocabulary/aq/equivalencedemonstrated/ref');
INSERT INTO public.eea_equivalencedemonstrated (id, label, notation, uri) VALUES ('yes', 'Equivalence demonstrated', 'Equivalence demonstrated', 'http://dd.eionet.europa.eu/vocabulary/aq/equivalencedemonstrated/yes');

INSERT INTO public.eea_exceedancedescription (id, label) VALUES (1, 'Base');
INSERT INTO public.eea_exceedancedescription (id, label) VALUES (2, 'Adjustment');
INSERT INTO public.eea_exceedancedescription (id, label) VALUES (3, 'Final');

INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S1', 'Heavily trafficked urban centre', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S1');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S10', 'Transport of air pollution originating from sources outside the Member State', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S10');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S11', 'Local petrol station', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S11');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S12', 'Parking facility', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S12');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S13', 'Benzene storage', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S13');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S16', 'Favourable meteorological conditions for ozone formation', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S16');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S17', 'Emissions due to public works and construction in the vicinity', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S17');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S2', 'Proximity to a major road', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S2');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S3', 'Local industry including power production', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S3');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S4', 'Quarrying or mining activities', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S4');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S5', 'Domestic heating', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S5');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S6', 'Accidental emission from industrial source', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S6');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S7', 'Accidental emission from non-industrial source', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S7');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S8', 'Natural source(s) or natural event(s)', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S8');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S9', 'Winter sanding of roads', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S9');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('other', 'Other, please specify', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/other');
INSERT INTO public.eea_exceedancereason (id, label, uri) VALUES ('S18', 'Use of studded tyres', 'http://dd.eionet.europa.eu/vocabulary/aq/exceedancereason/S18');

INSERT INTO public.eea_exceedancetype (id, label) VALUES (1, 'numberExceedances');
INSERT INTO public.eea_exceedancetype (id, label) VALUES (2, 'numericalExceedance');
INSERT INTO public.eea_exceedancetype (id, label) VALUES (3, 'percentileExceedance');

INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('AE22-PM2.5', 'AE22 Aethalometer with PM2.5 cyclone', 'AE22 Aethalometer with PM2.5 cyclone', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/AE22-PM2.5');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('AE31', 'AE31 Aethalometer', 'AE31 Aethalometer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/AE31');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('AE33', 'AE33 Aethalometer', 'AE33 Aethalometer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/AE33');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('AIRTOXICA73022', 'Chromatotec AirTOXIC BTX PID - A73022', 'Chromatotec AirTOXIC BTX PID - A73022', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/AIRTOXICA73022');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ANNOX', 'ANNOX', 'ANNOX', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ANNOX');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API', 'Teledyne API undertermined', 'Teledyne API undertermined', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API100', 'Teledyne API 100 UV Fluorescent SO2 Analyser', 'Teledyne API 100 UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API100');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API100A', 'Teledyne API 100A UV Fluorescent SO2 Analyser', 'Teledyne API 100A UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API100A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API100E', 'Teledyne API 100E UV Fluorescent SO2 Analyser', 'Teledyne API 100E UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API100E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API101', 'Teledyne API 101 UV Fluorescent SO2 Analyser', 'Teledyne API 101 UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API101');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API101A', 'Teledyne API 101A UV Fluorescent SO2 Analyser', 'Teledyne API 101A UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API101A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200', 'Teledyne API 200 chemiluminescent NOx analyser', 'Teledyne API 200 chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200A', 'Teledyne API 200A chemiluminescent NOx analyser', 'Teledyne API 200A chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200AU', 'TELEDYNE API 200AU', 'TELEDYNE API 200AU', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200AU');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200E', 'Teledyne API 200E chemiluminescent NOx analyser', 'Teledyne API 200E chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200EU', 'Teledyne API 200EU chemiluminescent NOx analyser', 'Teledyne API 200EU chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200EU');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200EU-BL', 'Teledyne API 200EU chemiluminescent NOx analyser - blue light', 'Teledyne API 200EU chemiluminescent NOx analyser - blue light', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200EU-BL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API200UP', 'Teledyne API 200UP chemiluminescent NOx analyser', 'Teledyne API 200UP chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API200UP');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API201A', 'Teledyne API 200A chemiluminescent NOx analyser', 'Teledyne API 200A chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API201A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API300', 'Teledyne API 300 gas filter correlation CO analyser', 'Teledyne API 300 gas filter correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API300A', 'Teledyne API 300A gas filter correlation CO analyser', 'Teledyne API 300A gas filter correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API300A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API300E', 'Teledyne API 300E gas filter correlation CO analyser', 'Teledyne API 300E gas filter correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API300E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API400', 'Teledyne API 400 UV photometric O3 analyser', 'Teledyne API 400 UV photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API400');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API400A', 'Teledyne API 400A UV photometric O3 analyser', 'Teledyne API 400A UV photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API400A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('API400E', 'Teledyne API 400E UV photometric O3 analyser', 'Teledyne API 400E UV photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/API400E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIM100E', 'Teledyne API M100E UV Fluorescent SO2 Analyser', 'Teledyne API M100E UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIM100E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIM200E', 'Teledyne API M200E chemiluminescent NOx analyser', 'Teledyne API M200E chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIM200E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIM300E', 'Teledyne API M300E gas filter correlation CO analyser', 'Teledyne API M300E gas filter correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIM300E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIM400E', 'Teledyne API M400E UV photometric O3 analyser', 'Teledyne API M400E UV photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIM400E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIT100', 'Teledyne API T100 UV Fluorescent SO2 Analyser', 'Teledyne API T100 UV Fluorescent SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIT100');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIT200', 'Teledyne API T200 chemiluminescent NOx analyser', 'Teledyne API T200 chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIT200');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIT200U', 'Teledyne API T200U chemiluminescent NOx analyser', 'Teledyne API T200U chemiluminescent NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIT200U');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIT300', 'Teledyne API T300 gas filter correlation CO analyser', 'Teledyne API T300 gas filter correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIT300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('APIT400', 'Teledyne API T400 UV photometric O3 analyser', 'Teledyne API T400 UV photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/APIT400');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('BAM1020', 'MetOne BAM-1020', 'MetOne BAM-1020', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/BAM1020');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('BAM1020heated', 'MetOne BAM-1020 heated', 'MetOne BAM-1020 heated', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/BAM1020heated');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('BAM1020unheated', 'MetOne BAM-1020 unheated', 'MetOne BAM-1020 unheated', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/BAM1020unheated');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('CP7001-BTX', 'Chrompack   BTX  CP7001 Monitor', 'Chrompack   BTX  CP7001 Monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/CP7001-BTX');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('DELTA', 'DELTA', 'DELTA', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/DELTA');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Ecophysics-CLD700AL', 'Eco Physics CLD 700 AL', 'Eco Physics CLD 700 AL', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Ecophysics-CLD700AL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Ecophysics-CLD780TR', 'Eco Physics CLD 780 TR', 'Eco Physics CLD 780 TR', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Ecophysics-CLD780TR');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Enviro1003RS', 'Environnement S.A. Model 1003-RS O3', 'Environnement S.A. Model 1003-RS O3', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Enviro1003RS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('F-701-20', 'F-701-20 Verewa / Durag', 'F-701-20 Verewa / Durag', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/F-701-20');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('FIDAS200', 'Palas model FIDAS 200', 'Palas model FIDAS 200', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/FIDAS200');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('FIDAS200E', 'Palas model FIDAS 200E', 'Palas model FIDAS 200E', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/FIDAS200E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('FIDAS200S', 'Palas model FIDAS 200S', 'Palas model FIDAS 200S', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/FIDAS200S');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC5000BTX-FID', 'AMA GC5000 BTX Type FID', 'AMA GC5000 BTX Type FID', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC5000BTX-FID');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC5000BTX-PID', 'AMA GC5000 BTX Type PID', 'AMA GC5000 BTX Type PID', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC5000BTX-PID');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC855BTX', 'SINTECH SPECTRAS BTX GC 855 series undetermined', 'SINTECH SPECTRAS BTX GC 855 series undetermined', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC855BTX');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC855BTX-600', 'SINTECH SPECTRAS BTX GC 855 serie 600', 'SINTECH SPECTRAS BTX GC 855 serie 600', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC855BTX-600');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC955', 'SYNTECH SPECTRAS GC 955 series undetermined', 'SYNTECH SPECTRAS GC 955 series undetermined', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC955');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC955-600', 'SYNTECH SPECTRAS GC 955-600', 'SYNTECH SPECTRAS GC 955-600', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC955-600');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GC955-800', 'SYNTECH SPECTRAS GC 955-800', 'SYNTECH SPECTRAS GC 955-800', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GC955-800');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM107', 'GRIMM model EDM 107 for PM10, PM2.5, PM1 and TC', 'GRIMM model EDM 107 for PM10, PM2.5, PM1 and TC', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM107');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM180', 'GRIMM model EDM 180 for PM10 and PM2.5', 'GRIMM model EDM 180 for PM10 and PM2.5', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM180');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM180C', 'GRIMM model EDM 180-C for PM10 and PM2.5', 'GRIMM model EDM 180-C for PM10 and PM2.5', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM180C');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM180D', 'GRIMM model EDM 180-D for PM10, PM2.5, PM1 and TC', 'GRIMM model EDM 180-D for PM10, PM2.5, PM1 and TC', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM180D');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM180MC', 'GRIMM model EDM 180-MC for PM10, PM2.5, PM1, TC and 31 size channels', 'GRIMM model EDM 180-MC for PM10, PM2.5, PM1, TC and 31 size channels', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM180MC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('GRIMM-EDM365', 'GRIMM model EDM 365 for PM10, PM2.5, PM1 and TC', 'GRIMM model EDM 365 for PM10, PM2.5, PM1 and TC', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/GRIMM-EDM365');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('IL-Punkkinen', 'IL-Punkkinen for NO2/NO hourly measurements', 'IL-Punkkinen for NO2/NO hourly measurements', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/IL-Punkkinen');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML', 'ML', 'ML', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML2010', 'Monitor Labs model 2010 O3 analyser', 'Monitor Labs model 2010 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML2010');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML2030', 'Monitor Labs model 2030 CO analyser', 'Monitor Labs model 2030 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML2030');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML2041', 'Monitor Labs model 2041 NOx analyser', 'Monitor Labs model 2041 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML2041');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML2050', 'Monitor Labs model 2050 SO2 analyser', 'Monitor Labs model 2050 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML2050');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8410', 'Monitor Labs model 8410 NOx analyser', 'Monitor Labs model 8410 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8410');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8440', 'Monitor Labs model 8440 NOx analyser', 'Monitor Labs model 8440 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8440');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8441', 'Monitor Labs model 8841 NOx analyser', 'Monitor Labs model 8841 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8441');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8810', 'Monitor Labs model 8810 O3 analyser', 'Monitor Labs model 8810 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8810');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8830', 'Monitor Labs model 8830 CO analyser', 'Monitor Labs model 8830 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8830');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8831', 'Monitor Labs model 8831 CO analyser', 'Monitor Labs model 8831 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8831');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8840', 'Monitor Labs model 8840 NOx analyser', 'Monitor Labs model 8840 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8840');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8841', 'Monitor Labs model 8841 NOx analyser', 'Monitor Labs model 8841 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8841');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8850', 'Monitor Labs model 8850 SO2 analyser', 'Monitor Labs model 8850 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8850');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8850M', 'Monitor Labs model 8850M SO2 analyser', 'Monitor Labs model 8850M SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8850M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8850S', 'Monitor Labs model 8850S SO2 analyser', 'Monitor Labs model 8850S SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8850S');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8930', 'Monitor Labs model 8930 CO analyser', 'Monitor Labs model 8930 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8930');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML8941A', 'Monitor Labs model 8941A NOx analyser', 'Monitor Labs model 8941A NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML8941A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9800', 'Monitor Labs model 9800', 'Monitor Labs model 9800', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9800');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9810', 'Monitor Labs model 9810 O3 analyser', 'Monitor Labs model 9810 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9810');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9810A', 'Monitor Labs model 9810A O3 analyser', 'Monitor Labs model 9810A O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9810A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9810B', 'Monitor Labs model 9810B O3 analyser', 'Monitor Labs model 9810B O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9810B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9811', 'Monitor Labs model 9811 O3 analyser', 'Monitor Labs model 9811 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9811');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9812', 'Monitor Labs model 9812 O3 analyser', 'Monitor Labs model 9812 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9812');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9830', 'Monitor Labs model 9830 CO analyser', 'Monitor Labs model 9830 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9830');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9830B', 'Monitor Labs model 9830B CO analyser', 'Monitor Labs model 9830B CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9830B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9832', 'Monitor Labs model 9832 CO analyser', 'Monitor Labs model 9832 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9832');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9840', 'Monitor Labs model 9840 NOx analyser', 'Monitor Labs model 9840 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9840');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9841', 'Monitor Labs model 9841 NOx analyser', 'Monitor Labs model 9841 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9841');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9841A', 'Monitor Labs model 9841A NOx analyser', 'Monitor Labs model 9841A NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9841A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9841B', 'Monitor Labs model 9841B NOx analyser', 'Monitor Labs model 9841B NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9841B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9841T', 'Monitor Labs model 9841T NOx analyser', 'Monitor Labs model 9841T NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9841T');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9850', 'Monitor Labs model 9850 SO2 analyser', 'Monitor Labs model 9850 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9850');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML9850B', 'Monitor Labs model 9850B SO2 analyser', 'Monitor Labs model 9850B SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML9850B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('PicarroG2401', 'Picarro G2401 (used for CO measurement)', 'Picarro G2401 (used for CO measurement)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/PicarroG2401');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('SFIO342M', 'SFI O342M', 'SFI O342M', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/SFIO342M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('SRI8610', 'SRI 8610', 'SRI 8610', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/SRI8610');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('SWAM5aDual', 'SWAM 5a Dual channel monitor', 'SWAM 5a Dual channel monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/SWAM5aDual');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('SWAM5aSingle', 'SWAM 5a Single channel monitor', 'SWAM 5a Single channel monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/SWAM5aSingle');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Serinus10', 'Serinus 10 O3', 'Serinus 10 O3', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Serinus10');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Serinus30', 'Serinus30 CO', 'Serinus30 CO', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Serinus30');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('Serinus50', 'Serinus 50 SO2', 'Serinus 50 SO2', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/Serinus50');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1400', 'TEOM 1400', 'TEOM 1400', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1400');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1400A', 'TEOM 1400A', 'TEOM 1400A', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1400A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1400AB', 'TEOM 1400AB', 'TEOM 1400AB', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1400AB');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1400AB-FDMS', 'TEOM 1400AB with FDMS module (8500)', 'TEOM 1400AB with FDMS module (8500)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1400AB-FDMS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1400FDMS-8500B-CB', 'TEOM 1400 FDMS + 8500 B or CB Dryer', 'TEOM 1400 FDMS + 8500 B or CB Dryer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1400FDMS-8500B-CB');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1405', 'TEOM 1405', 'TEOM 1405', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1405');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1405D', 'TEOM 1405D', 'TEOM 1405D', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1405D');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1405DF-FDMS', 'TEOM 1405DF with FDMS Dichotomous monitor for PM2.5 & PM10', 'TEOM 1405DF with FDMS Dichotomous monitor for PM2.5 & PM10', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1405DF-FDMS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TEOM1405F-FDMS', 'TEOM 1405F with FDMS', 'TEOM 1405F with FDMS', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TEOM1405F-FDMS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('THERMO450i', 'THERMO 450i', 'THERMO 450i', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/THERMO450i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TSI3022ACPC', 'TSI 3022A CPC', 'TSI 3022A CPC', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TSI3022ACPC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('TSI3936SMPS', 'TSI 3936 SMPS', 'TSI 3936 SMPS', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/TSI3936SMPS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('URG', 'URG', 'URG', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/URG');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('VOC71M', 'Environnement VOC71M', 'Environnement VOC71M', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/VOC71M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('VOC72M', 'Environnement VOC72M', 'Environnement VOC72M', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/VOC72M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('WoesthoffU3S', 'Woesthoff U3S', 'Woesthoff U3S', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/WoesthoffU3S');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('agilentHP6890', 'agilent HP 6890', 'agilent HP 6890', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/agilentHP6890');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('airmoOzone', 'CHROMATOTEC airmOzone', 'CHROMATOTEC airmOzone', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/airmoOzone');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('airmoVOC_BTX', 'airmoVOC BTX', 'airmoVOC BTX', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/airmoVOC_BTX');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('airmoVOC_BTX1000', 'airmotec BTX 1000', 'airmotec BTX 1000', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/airmoVOC_BTX1000');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('airpointer', 'airpointer', 'airpointer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/airpointer');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('alpha400', 'SYNSPEC model Alpha 400', 'SYNSPEC model Alpha 400', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/alpha400');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenFH621N', 'Andersen/GMW Model  FH621-N Beta Monitor', 'Andersen/GMW Model  FH621-N Beta Monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenFH621N');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenFH62IN', 'Andersen/GMW Model FH62I-N Beta Monitor', 'Andersen/GMW Model FH62I-N Beta Monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenFH62IN');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenFH62IR', 'Thermo Andersen ESM FH 62 I-R', 'Thermo Andersen ESM FH 62 I-R', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenFH62IR');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenGPS-1-modif', 'Modified Andersen GPS-1 sampler', 'Modified Andersen GPS-1 sampler', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenGPS-1-modif');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenHVS', 'Andersen/GMW generic High-Volume Air Sampler', 'Andersen/GMW generic High-Volume Air Sampler', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenHVS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('bendix8101c', 'Bendix/Combustion Engineering Model 8101-C Oxides of Nitrogen Analyze', 'Bendix/Combustion Engineering Model 8101-C Oxides of Nitrogen Analyze', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/bendix8101c');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('csi1600', 'Columbia Scientific Industries Models 1600', 'Columbia Scientific Industries Models 1600', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/csi1600');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('andersenFH62C14', 'Thermo Andersen Series FH 62 C14 Continuous PM10 Ambient Particulate Monitor', 'Thermo Andersen Series FH 62 C14 Continuous PM10 Ambient Particulate Monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/andersenFH62C14');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('csi5600', 'Columbia Scientific Industries Models 5600', 'Columbia Scientific Industries Models 5600', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/csi5600');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi', 'DASIBI', 'DASIBI', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1003', 'DASIBI 1003 O3 analyser', 'DASIBI 1003 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1003');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1003PC', 'DASIBI 1003-PC O3 analyser', 'DASIBI 1003-PC O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1003PC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1003RS', 'DASIBI 1003-RS O3 analyser', 'DASIBI 1003-RS O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1003RS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1008', 'DASIBI 1008 O3 analyser', 'DASIBI 1008 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1008');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1008AH', 'DASIBI 1008-AH O3 analyser', 'DASIBI 1008-AH O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1008AH');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1008PC', 'DASIBI 1008-PC O3 analyser', 'DASIBI 1008-PC O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1008PC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1008RS', 'DASIBI 1008-RS O3 analyser', 'DASIBI 1008-RS O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1008RS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi1108', 'DASIBI 1108 O3 analyser', 'DASIBI 1108 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi1108');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi2108', 'DASIBI 2108 NOx analyser', 'DASIBI 2108 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi2108');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi3008', 'DASIBI 3008 CO analyser', 'DASIBI 3008 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi3008');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi4108', 'DASIBI 4108 SO2 analyser', 'DASIBI 4108 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi4108');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi5014', 'DASIBI 5014', 'DASIBI 5014', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi5014');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('dasibi7001', 'DASIBI 7001', 'DASIBI 7001', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/dasibi7001');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('eberlineFH62-1', 'EBERLINE model FH 62-1', 'EBERLINE model FH 62-1', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/eberlineFH62-1');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enrivoAC21M', 'Environnement S.A. Model AC21M NO2 Analyzer', 'Environnement S.A. Model AC21M NO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enrivoAC21M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enrivoAC30M', 'Environnement S.A. Model AC30M NO2 Analyzer', 'Environnement S.A. Model AC30M NO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enrivoAC30M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enrivoAC31M', 'Environnement S.A. Model AC31M NO2 Analyzer', 'Environnement S.A. Model AC31M NO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enrivoAC31M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enrivoAC32M', 'Environnement S.A. Model AC32M NO2 Analyzer', 'Environnement S.A. Model AC32M NO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enrivoAC32M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroAC32E', 'Environnement S.A. Model AC32E NO2 Analyzer', 'Environnement S.A. Model AC32E NO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroAC32E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroAF20M', 'Environnement S.A. Model AF20M SO2 Analyzer', 'Environnement S.A. Model AF20M SO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroAF20M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroAF21M', 'Environnement S.A. Model AF21M SO2 Analyzer', 'Environnement S.A. Model AF21M SO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroAF21M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroAF22M', 'Environnement S.A. Model AF22M SO2 Analyzer', 'Environnement S.A. Model AF22M SO2 Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroAF22M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroAS32M', 'Environnement S.A. Model AS32M Nitrogen Dioxide Analyzer', 'Environnement S.A. Model AS32M Nitrogen Dioxide Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroAS32M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroCO10M', 'Environnement S.A. Model CO10M CO Analyzer', 'Environnement S.A. Model CO10M CO Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroCO10M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroCO11M', 'Environnement S.A. Model CO11M CO Analyzer', 'Environnement S.A. Model CO11M CO Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroCO11M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroCO12E', 'Environnement S.A. Model CO12E CO Analyzer', 'Environnement S.A. Model CO12E CO Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroCO12E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroCO12M', 'Environnement S.A. Model CO12M CO Analyzer', 'Environnement S.A. Model CO12M CO Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroCO12M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroMP101M', 'Environnement S.A. Model MP101M (may be used for PM10 and PM2.5)', 'Environnement S.A. Model MP101M (may be used for PM10 and PM2.5)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroMP101M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroMP2.5M', 'Environnement S.A. Model MP2.5M undefined', 'Environnement S.A. Model MP2.5M undefined', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroMP2.5M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroMPSI100', 'Environnement S.A. Model MPSI 100', 'Environnement S.A. Model MPSI 100', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroMPSI100');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroO331M', 'enviroO331M', 'enviroO331M', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroO331M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroO341M', 'Environnement S.A. Model O341M UV Ozone Analyzer', 'Environnement S.A. Model O341M UV Ozone Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroO341M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroO342E', 'Environnement S.A. Model O342E UV Ozone Analyzer', 'Environnement S.A. Model O342E UV Ozone Analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroO342E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroO342M', 'Environnement S.A. Model O342M UV Ozone Analyze', 'Environnement S.A. Model O342M UV Ozone Analyze', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroO342M');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('enviroSANOA', 'Environnement S.A. SANOA Multigas Longpath Monitoring System', 'Environnement S.A. SANOA Multigas Longpath Monitoring System', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/enviroSANOA');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPDA350', 'Horiba model APDA 350 TSP analyser', 'Horiba model APDA 350 TSP analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPDA350');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPDA350E', 'Horiba model APDA 350E TSP analyser', 'Horiba model APDA 350E TSP analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPDA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPDA351', 'Horiba model APDA 351 TSP analyser', 'Horiba model APDA 351 TSP analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPDA351');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPDA351E', 'Horiba model APDA 351E TSP analyser', 'Horiba model APDA 351E TSP analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPDA351E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPDA371', 'Horiba model APDA 371', 'Horiba model APDA 371', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPDA371');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPHA350E', 'Horiba model APHA 360E hydrocarbons analyser', 'Horiba model APHA 360E hydrocarbons analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPHA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPHA360', 'Horiba model APHA 360 hydrocarbons analyser', 'Horiba model APHA 360 hydrocarbons analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPHA360');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPHA370', 'Horiba model APHA 370 hydrocarbons analyser', 'Horiba model APHA 370 hydrocarbons analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPHA370');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA300', 'Horiba model APMA 300 CO analyser', 'Horiba model APMA 300 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA300E', 'Horiba model APMA 300E CO analyser', 'Horiba model APMA 300E CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA300E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA350', 'Horiba model APMA 350 CO analyser', 'Horiba model APMA 350 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA350');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA350E', 'Horiba model APMA 350E CO analyser', 'Horiba model APMA 350E CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA360', 'Horiba model APMA 360 CO analyser', 'Horiba model APMA 360 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA360');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA360CE', 'Horiba model APMA 360CE CO analyser', 'Horiba model APMA 360CE CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA360CE');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA360E', 'Horiba model APMA 360E CO analyser', 'Horiba model APMA 360E CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA360E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPMA370', 'Horiba model APMA 370 CO analyser', 'Horiba model APMA 370 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPMA370');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA300', 'Horiba model APNA 300 NOx analyser', 'Horiba model APNA 300 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA300E', 'Horiba model APNA 300E NOx analyser', 'Horiba model APNA 300E NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA300E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA350', 'Horiba model APNA 350 NOx analyser', 'Horiba model APNA 350 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA350');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA350E', 'Horiba model APNA 350E NOx analyser', 'Horiba model APNA 350E NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA360', 'Horiba model APNA 360 NOx analyser', 'Horiba model APNA 360 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA360');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA360E', 'Horiba model APNA 360E NOx analyser', 'Horiba model APNA 360E NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA360E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPNA370', 'Horiba model APNA 370 NOx analyser', 'Horiba model APNA 370 NOx analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPNA370');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA300', 'Horiba model APOA 300 O3 analyser', 'Horiba model APOA 300 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA350', 'Horiba model APOA 350 O3 analyser', 'Horiba model APOA 350 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA350');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA350E', 'Horiba model APOA 350E O3 analyser', 'Horiba model APOA 350E O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA360', 'Horiba model APOA 360 O3 analyser', 'Horiba model APOA 360 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA360');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA360E', 'Horiba model APOA 350E O3 analyser', 'Horiba model APOA 350E O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA360E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPOA370', 'Horiba model APOA 370 O3 analyser', 'Horiba model APOA 370 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPOA370');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA300', 'Horiba model APSA 300 SO2 analyser', 'Horiba model APSA 300 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA300');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA350', 'Horiba model APSA 350 SO2 analyser', 'Horiba model APSA 350 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA350');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA350E', 'Horiba model APSA 350E SO2 analyser', 'Horiba model APSA 350E SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA350E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA360', 'Horiba model APSA 360 SO2 analyser', 'Horiba model APSA 360 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA360');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA360A', 'Horiba model APSA 360A SO2 analyser', 'Horiba model APSA 360A SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA360A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA360E', 'Horiba model APSA 360E SO2 analyser', 'Horiba model APSA 360E SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA360E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaAPSA370', 'Horiba model APSA 370 SO2 analyser', 'Horiba model APSA 370 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaAPSA370');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('horibaFH621R', 'ONLY USED IN ONE STATION IN RS', 'ONLY USED IN ONE STATION IN RS', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/horibaFH621R');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('kimoto168s', 'KIMOTO 168s', 'KIMOTO 168s', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/kimoto168s');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('marga', 'Marga', 'Marga', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/marga');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('mcv30ql', 'MCV 30-QL', 'MCV 30-QL', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/mcv30ql');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('mcv48auv', 'MCV 48-AUV', 'MCV 48-AUV', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/mcv48auv');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('mcv64fuv', 'MCV 64-FUV', 'MCV 64-FUV', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/mcv64fuv');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('mcvCAV-AMSb', 'MCV CAV-A/MSb Captador d''Alt Volum Sequencial', 'MCV CAV-A/MSb Captador d''Alt Volum Sequencial', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/mcvCAV-AMSb');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('mcvCAV-Amb', 'MCV CAV-A/mb Captador d''Alt Volum', 'MCV CAV-A/mb Captador d''Alt Volum', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/mcvCAV-Amb');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('meloySA700', 'Meloy Model SA 700 Fluorescence Sulfur Dioxide Analyze', 'Meloy Model SA 700 Fluorescence Sulfur Dioxide Analyze', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/meloySA700');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('multigasMMS', 'Multi-gas Micro Monitoring station (MMS) Portable version', 'Multi-gas Micro Monitoring station (MMS) Portable version', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/multigasMMS');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('opsisAR500', 'Opsis AR500 Open path monitor', 'Opsis AR500 Open path monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/opsisAR500');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('opsisAR500-ER110', 'Opsis AR500 Open path monitor with ER 110', 'Opsis AR500 Open path monitor with ER 110', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/opsisAR500-ER110');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('opsisAR500-ER120', 'Opsis AR500 Open path monitor with ER 120', 'Opsis AR500 Open path monitor with ER 120', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/opsisAR500-ER120');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('opsisAR500-ER150', 'Opsis AR500 Open path monitor with ER 150', 'Opsis AR500 Open path monitor with ER 150', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/opsisAR500-ER150');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('opsisSM200', 'Opsis SM200 Particulate Analyser with PM2.5 & PM10 Heads', 'Opsis SM200 Particulate Analyser with PM2.5 & PM10 Heads', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/opsisSM200');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('osiris', 'Osiris Turnkey Instruments', 'Osiris Turnkey Instruments', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/osiris');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('other', 'Other', 'Other', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/other');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('perkinelmerC500', 'Perkin Elmer Clarus 500', 'Perkin Elmer Clarus 500', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/perkinelmerC500');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('perkinelmerTurbomatrixDesorber', 'Perking Elmer Turbomatrix Desorber', 'Perking Elmer Turbomatrix Desorber', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/perkinelmerTurbomatrixDesorber');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50031', 'PHILIPS K50031 Chromatographic Analyser', 'PHILIPS K50031 Chromatographic Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50031');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50033', 'PHILIPS K50033 API 100E', 'PHILIPS K50033 API 100E', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50033');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50034', 'PHILIPS K50034 API 200A', 'PHILIPS K50034 API 200A', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50034');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50093', 'PHILIPS K50093 API 300A', 'PHILIPS K50093 API 300A', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50093');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50094', 'PHILIPS K50094 API 400', 'PHILIPS K50094 API 400', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50094');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50102', 'PHILIPS K50102 NO', 'PHILIPS K50102 NO', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50102');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50109', 'PHILIPS K50109/00 Gas Filter Correlation CO analyser', 'PHILIPS K50109/00 Gas Filter Correlation CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50109');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50110', 'PHILIPS K50110/00 UV Photometric O3 analyser', 'PHILIPS K50110/00 UV Photometric O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50110');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50129', 'PHILIPS K50129 unknown', 'PHILIPS K50129 unknown', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50129');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50130', 'PHILIPS K50130 unknown', 'PHILIPS K50130 unknown', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50130');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50206', 'PHILIPS K50206/00 Pulsed Fluorescence SO2 analyser', 'PHILIPS K50206/00 Pulsed Fluorescence SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50206');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsK50235', 'PHILIPS K50235/00 NO-NOx-NO2 analyser', 'PHILIPS K50235/00 NO-NOx-NO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsK50235');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsPW9755', 'PHILIPS PW9755/00 SO2 Analyser', 'PHILIPS PW9755/00 SO2 Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsPW9755');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('philipsPW9762', 'PHILIPS PW9762/00 NO/NO2/NOX Analyser', 'PHILIPS PW9762/00 NO/NO2/NOX Analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/philipsPW9762');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('picarroG2302', 'Picarro G2302', 'Picarro G2302', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/picarroG2302');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('picarroG2303', 'Picarro G2303', 'Picarro G2303', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/picarroG2303');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('serinus40', 'serinus 40 Nox', 'serinus 40 Nox', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/serinus40');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('serinus40NH3', 'serinus 40 with NH3 converter', 'serinus 40 with NH3 converter', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/serinus40NH3');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('sunsetTOCA', 'EC/OC measurements Sunset Laboratory Inc Thermal / Optical Carbon Analyser (near-real time)', 'EC/OC measurements Sunset Laboratory Inc Thermal / Optical Carbon Analyser (near-real time)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/sunsetTOCA');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('tekran2537A', 'Tekran mercury analyser 2537A', 'Tekran mercury analyser 2537A', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/tekran2537A');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('tekran2537B', 'Tekran mercury analyser 2537B', 'Tekran mercury analyser 2537B', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/tekran2537B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('tekran2537X', 'Tekran mercury analyser 2537X', 'Tekran mercury analyser 2537X', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/tekran2537X');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo14B', 'Thermo model 14B chemiluminescence NO-NO2-Nox', 'Thermo model 14B chemiluminescence NO-NO2-Nox', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo14B');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo14B-E', 'Thermo model 14B/E chemiluminescence NO-NO2-Nox', 'Thermo model 14B/E chemiluminescence NO-NO2-Nox', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo14B-E');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo14BE', 'Thermo model 14B/E chemiluminescence NO-NO2-Nox', 'Thermo model 14B/E chemiluminescence NO-NO2-Nox', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo14BE');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42', 'Thermo model 42 NO/Nox analyser', 'Thermo model 42 NO/Nox analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42c', 'Thermo model 42c NO/Nox analyser', 'Thermo model 42c NO/Nox analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42c');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42c-TL', 'Thermo model 42C-TL (Trace level Nox)', 'Thermo model 42C-TL (Trace level Nox)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42c-TL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42i', 'Thermo model 42i NO/Nox analyser', 'Thermo model 42i NO/Nox analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42i-BL', 'Thermo model 42i NO/NOx analyser - blue light', 'Thermo model 42i NO/NOx analyser - blue light', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42i-BL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42i-TL', 'Thermo model 42i-TL (Trace level Nox)', 'Thermo model 42i-TL (Trace level Nox)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42i-TL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42s', 'Thermo model 42s NO/Nox analyser', 'Thermo model 42s NO/Nox analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42s');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo42w', 'Thermo model 42w NO/Nox analyser', 'Thermo model 42w NO/Nox analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo42w');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43', 'Thermo model 43 SO2 analyser', 'Thermo model 43 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43CTL', 'Thermo model 43c-TL SO2 analyser', 'Thermo model 43c-TL SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43CTL');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43a', 'Thermo model 43a SO2 analyser', 'Thermo model 43a SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43a');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43b', 'Thermo model 43b SO2 analyser', 'Thermo model 43b SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43b');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43bs', 'Thermo model 43bs SO2 analyser', 'Thermo model 43bs SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43bs');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43c', 'Thermo model 43c SO2 analyser', 'Thermo model 43c SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43c');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43h', 'Thermo model 43h pulsed fluorescence SO2 analyser', 'Thermo model 43h pulsed fluorescence SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43h');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43i', 'Thermo model 43i SO2 analyser', 'Thermo model 43i SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43i-TLE', 'Thermo model 43i-TLE (Enhanced Trace Level)', 'Thermo model 43i-TLE (Enhanced Trace Level)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43i-TLE');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43s', 'Thermo model 43s SO2 analyser', 'Thermo model 43s SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43s');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo43w', 'Thermo model 43w SO2 analyser', 'Thermo model 43w SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo43w');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48', 'Thermo model 48 CO analyser', 'Thermo model 48 CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48-GFC', 'Thermo model 48 CO analyser (gas filter correlation)', 'Thermo model 48 CO analyser (gas filter correlation)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48-GFC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48c', 'Thermo model 48c CO analyser', 'Thermo model 48c CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48c');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48i', 'Thermo model 48i CO analyser', 'Thermo model 48i CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48i-TLE', 'Thermo model 48i-TLE (Enhanced Trace Level)', 'Thermo model 48i-TLE (Enhanced Trace Level)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48i-TLE');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo48w', 'Thermo model 48w CO analyser', 'Thermo model 48w CO analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo48w');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo49', 'Thermo model 49 O3 analyser', 'Thermo model 49 O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo49');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo49c', 'Thermo model 49c O3 analyser', 'Thermo model 49c O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo49c');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo49cps', 'Thermo 49 CPS Ozone Primary Standard', 'Thermo 49 CPS Ozone Primary Standard', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo49cps');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo49i', 'Thermo model 49i O3 analyser', 'Thermo model 49i O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo49i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo49w', 'Thermo model 49w O3 analyser', 'Thermo model 49w O3 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo49w');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo5014i', 'Thermo 5014i Beta Continuous Ambient Particulate Monitor', 'Thermo 5014i Beta Continuous Ambient Particulate Monitor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo5014i');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermo5030SHARP', 'Thermo model 5030 SHARP Particular Monitor with PM10 & PM2.5 heads', 'Thermo model 5030 SHARP Particular Monitor with PM10 & PM2.5 heads', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermo5030SHARP');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermoAorC', 'Thermo a or c-series', 'Thermo a or c-series', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermoAorC');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('thermoI', 'Thermo i-series', 'Thermo i-series', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/thermoI');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('undetermined', 'too generic', 'too generic', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/undetermined');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('unknown', 'Unknown', 'Unknown', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/unknown');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('unor6N', 'Maihak Unor 6N', 'Maihak Unor 6N', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/unor6N');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('ML2040', 'Monitor Labs model 2040 SO2 analyser', 'Monitor Labs model 2040 SO2 analyser', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/ML2040');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('aerisAE2041U', 'Aeris AE2041U', 'aerisAE2041U', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/aerisAE2041U');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('aerisAE2030U', 'Aeris AE2030U', 'aerisAE2030U', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/aerisAE2030U');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('aerisAE2050U', 'Aeris AE2050U', 'aerisAE2050U', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/aerisAE2050U');
INSERT INTO public.eea_measurementequipments (id, label, notation, uri) VALUES ('aerisAE2010U', 'Aeris AE2010U', 'aerisAE2010U', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementequipment/aerisAE2010U');

INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('BETA', 'Beta ray attenuation', 'Beta ray attenuation', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/BETA');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('CAPS', 'CAPS', 'CAPS', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/CAPS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('CPC', 'Condensation particle counter', 'Condensation particle counter', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/CPC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('CRDS', 'Cavity ring down spectroscopy', 'Cavity ring down spectroscopy', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/CRDS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('CV-AFS', 'Cold vapour atomic fluorescence spectrometry', 'Cold vapour atomic fluorescence spectrometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/CV-AFS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('DOAS', 'Differential Optical Absorption Spectroscopy (DOAS)', 'Differential Optical Absorption Spectroscopy (DOAS)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/DOAS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('FID', 'Flame ionization detection (FID)', 'Flame ionization detection (FID)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/FID');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('GC', 'Gas chromatography', 'Gas chromatography', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/GC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('GC-FID', 'Gas chromatography followed by flame ionization detection (GC-FID)', 'Gas chromatography followed by flame ionization detection (GC-FID)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/GC-FID');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('GC-MS', 'Gas chromatography followed by mass spectrometry (GC-MS)', 'Gas chromatography followed by mass spectrometry (GC-MS)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/GC-MS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('GC-PID', 'Gas chromatography followed by photo ionization detection (GC-PID)', 'Gas chromatography followed by photo ionization detection (GC-PID)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/GC-PID');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('IC', 'Ion chromatography', 'Ion chromatography', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/IC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('IR-GFC', 'Infrared gas filter correlation', 'Infrared gas filter correlation', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/IR-GFC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('NDIR', 'Non-dispersive infrared spectroscopy (NDIR)', 'Non-dispersive infrared spectroscopy (NDIR)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/NDIR');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('OPC-CMC', 'Optical particle counter + conversion to mass concentration', 'Optical particle counter + conversion to mass concentration', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/OPC-CMC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('SMPS', 'Scanning mobilty particle sizer (SMPS)', 'Scanning mobilty particle sizer (SMPS)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/SMPS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('SP', 'Spectrophotometry', 'Spectrophotometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/SP');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('TEOM', 'Tapered Element Oscillating Microbalance (TEOM)', 'Tapered Element Oscillating Microbalance (TEOM)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/TEOM');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('TEOM-FDMS', 'Tapered Element Oscillating Microbalance (TEOM) with Filter Dynamics Measurement System (FDMS)', 'Tapered Element Oscillating Microbalance (TEOM) with Filter Dynamics Measurement System (FDMS)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/TEOM-FDMS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('TEOM-corVolatile', 'Tapered Element Oscillating Microbalance (TEOM) + correction with estimated volatile fraction', 'Tapered Element Oscillating Microbalance (TEOM) + correction with estimated volatile fraction', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/TEOM-corVolatile');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('TO-ECOC', 'Thermo-optical EC/OC measurement', 'Thermo-optical EC/OC measurement', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/TO-ECOC');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('UV-FL', 'UV fluorescence', 'UV fluorescence', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/UV-FL');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('UV-P', 'Ultraviolet (UV) photometry', 'Ultraviolet (UV) photometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/UV-P');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('VUV', 'Vakuum-Ultraviolet (VUV) Spectrometry', 'Vakuum-Ultraviolet (VUV) Spectrometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/VUV');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('ZeemanAAS', 'Zeeman atomic absorption spectrometry (ZeemanAAS)', 'Zeeman atomic absorption spectrometry (ZeemanAAS)', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/ZeemanAAS');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('chemi', 'Chemiluminescence', 'Chemiluminescence', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/chemi');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('coulometry', 'Coulometry', 'Coulometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/coulometry');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('light-abs', 'Light absorption', 'Light absorption', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/light-abs');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('light-scat', 'Light scattering', 'Light scattering', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/light-scat');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('nephelometry', 'Nephelometry', 'Nephelometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/nephelometry');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('nephelometry+beta', 'Nephelometry + BETA', 'Nephelometry + BETA', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/nephelometry_beta');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('other', 'Other, please specify', 'Other, please specify', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/other');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('potentiometry', 'Potentiometry', 'Potentiometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/potentiometry');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('reflect', 'Reflectrometry', 'Reflectrometry', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/reflect');
INSERT INTO public.eea_measurementmethods (id, label, notation, uri) VALUES ('saltzman', 'Saltzman - colorimetric microdetermination of NO2', 'Saltzman - colorimetric microdetermination of NO2', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementmethod/saltzman');

-- ids are the URI's last segment, all four lowercase. Two of them used to be
-- camelCased ('continuousDataCollection', 'periodicDataCollection') while the other two
-- were not, so a database normalised by migration 016_vocabulary_id_normalisation.sql --
-- which derives the id from the URI -- disagreed with a fresh install on exactly those
-- two rows. Nothing references this table, so the spelling is free to be consistent.
INSERT INTO public.eea_measurementregimevalues (id, label, notation, uri) VALUES ('continuousdatacollection', 'continuous data collection', 'continuous data collection', 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/continuousdatacollection');
INSERT INTO public.eea_measurementregimevalues (id, label, notation, uri) VALUES ('demanddrivendatacollection', 'demand driven data collection', 'demand driven data collection', 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/demanddrivendatacollection');
INSERT INTO public.eea_measurementregimevalues (id, label, notation, uri) VALUES ('periodicdatacollection', 'periodic data collection', 'periodic data collection', 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/periodicdatacollection');
INSERT INTO public.eea_measurementregimevalues (id, label, notation, uri) VALUES ('onceoffdatacollection', 'once-off data collection', 'once-off data collection', 'http://inspire.ec.europa.eu/codelist/measurementregimevalue/onceoffdatacollection');

INSERT INTO public.eea_measurementtypes (id, label, notation, uri) VALUES ('active', 'Active sampling', 'Active sampling', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/active');
INSERT INTO public.eea_measurementtypes (id, label, notation, uri) VALUES ('automatic', 'Automatic analyzer', 'Automatic analyzer', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/automatic');
INSERT INTO public.eea_measurementtypes (id, label, notation, uri) VALUES ('passive', 'Passive sampling', 'Passive sampling', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/passive');
INSERT INTO public.eea_measurementtypes (id, label, notation, uri) VALUES ('remote', 'Remote sensor', 'Remote sensor', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/remote');
INSERT INTO public.eea_measurementtypes (id, label, notation, uri) VALUES ('unknown', 'Unknown', 'Unknown', 'http://dd.eionet.europa.eu/vocabulary/aq/measurementtype/unknown');

INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('biota', 'Biota', 'biota', 'http://inspire.ec.europa.eu/codelist/mediavalue/biota');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('air', 'Air', 'air', 'http://inspire.ec.europa.eu/codelist/MediaValue/air');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('sediment', 'Sediment', 'sediment', 'http://inspire.ec.europa.eu/codelist/mediavalue/sediment');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('landscape', 'Landscape', 'landscape', 'http://inspire.ec.europa.eu/codelist/mediavalue/landscape');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('waste', 'Waste', 'waste', 'http://inspire.ec.europa.eu/codelist/mediavalue/waste');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('soil-ground', 'Soil/ground', 'soil/ground', 'http://inspire.ec.europa.eu/codelist/mediavalue/soil-ground');
INSERT INTO public.eea_mediavalues (id, label, notation, uri) VALUES ('water', 'Water', 'water', 'http://inspire.ec.europa.eu/codelist/mediavalue/water');

INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('ALT', 'Alert threshold (ALT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ALT');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('CL', 'Critical level (CL)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/CL');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('ECO', 'Exposure concentration obligation (ECO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ECO');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('ERT', 'Exposure reduction target (ERT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ERT');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('INT', 'Information Threshold (INT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/INT');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('LTO', 'Long term objective (LTO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LTO');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('LV', 'Limit Value (LV)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LV');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('LVmaxMOT', 'Limit value plus maximum margin of', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LVmaxMOT');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('LVMOT', 'Limit value plus applicable margin of', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LVMOT');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('MO', 'Monitoring objective (MO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/MO');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('TV', 'Target Value (TV)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/TV');
INSERT INTO public.eea_objecttypes (id, label, uri) VALUES ('LV-S2', 'Limit Value (Stage II) for reporting PM2.5 only', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LV-S2');

-- AQR3 STA_05 NetworkOrganisationalLevel -> vocabulary/aq/administrativelevel.
-- These rows used to target eea_organisationallevels, a table that does not
-- exist in schema.sql (v3 leftover, and the ids were full URIs rather than the
-- v4 notation-as-id convention), so all six INSERTs failed on a fresh install
-- and eea_administrativelevels was left empty.
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('international', 'International', 'international', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/international');
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('local', 'Local', 'local', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/local');
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('localauthority', 'Local Authority', 'localauthority', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/localauthority');
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('municipality', 'Municipality', 'municipality', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/municipality');
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('national', 'National', 'national', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/national');
INSERT INTO public.eea_administrativelevels (id, label, notation, uri) VALUES ('regional', 'Regional', 'regional', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/regional');

-- AQR3 v5.02 new vocabularies (see sql/migrations/002_aqr3_v502_renames.sql)
INSERT INTO public.eea_resultencoding (id, label, notation, uri) VALUES ('inline', 'Inline (grid cells in the CSV)', 'inline', 'http://dd.eionet.europa.eu/vocabulary/aq/resultencoding/inline');
INSERT INTO public.eea_resultencoding (id, label, notation, uri) VALUES ('external', 'External (attached GEOTIFF)', 'external', 'http://dd.eionet.europa.eu/vocabulary/aq/resultencoding/external');

INSERT INTO public.eea_modelapplication (id, label, notation, uri) VALUES ('assessment', 'Assessment', 'assessment', 'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/assessment');
INSERT INTO public.eea_modelapplication (id, label, notation, uri) VALUES ('adjustment', 'Adjustment', 'adjustment', 'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/adjustment');
INSERT INTO public.eea_modelapplication (id, label, notation, uri) VALUES ('scenario', 'Scenario', 'scenario', 'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/scenario');
INSERT INTO public.eea_modelapplication (id, label, notation, uri) VALUES ('representativeness', 'Spatial representativeness', 'representativeness', 'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/representativeness');

-- EEA INSPIRE grid resolution steps in metres (see the guide's Introduction sheet)
INSERT INTO public.eea_spatialresolution (id, label, notation, uri) VALUES ('10', '10 m', '10', 'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/10');
INSERT INTO public.eea_spatialresolution (id, label, notation, uri) VALUES ('100', '100 m', '100', 'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/100');
INSERT INTO public.eea_spatialresolution (id, label, notation, uri) VALUES ('1000', '1000 m', '1000', 'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/1000');
INSERT INTO public.eea_spatialresolution (id, label, notation, uri) VALUES ('10000', '10000 m', '10000', 'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/10000');

INSERT INTO public.eea_srapplication (id, label, notation, uri) VALUES ('spo_sr', 'Sampling point representativeness area', 'spo_sr', 'http://dd.eionet.europa.eu/vocabulary/aq/SRapplication/spo_sr');
INSERT INTO public.eea_srapplication (id, label, notation, uri) VALUES ('exc_sr', 'Exceedance extent', 'exc_sr', 'http://dd.eionet.europa.eu/vocabulary/aq/SRapplication/exc_sr');

INSERT INTO public.eea_processtypevalues (id, label, notation, uri) VALUES ('sensorML', 'SensorML', 'SensorML', 'http://inspire.ec.europa.eu/codelist/processtypevalue/sensorML');
INSERT INTO public.eea_processtypevalues (id, label, notation, uri) VALUES ('process', 'Process', 'Process', 'http://inspire.ec.europa.eu/codelist/processtypevalue/process');

INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('H', 'Health', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/H');
INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('H-S1', 'Health (Stage 1)', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/H-S1');
INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('H-S2', 'Health (Stage 2)', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/H-S2');
INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('HV', 'Health and Vegetation', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/HV');
INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('NA', 'Not applicable', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/NA');
INSERT INTO public.eea_protectiontargets (id, label, uri) VALUES ('V', 'Vegetation', 'http://dd.eionet.europa.eu/vocabulary/aq/protectiontarget/V');

INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('daysAbove-3yr', 'Days in exceedance averaged over 3', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/daysAbove-3yr');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('hrsAbove', 'Hours in exceedance in a calendar year', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/hrsAbove');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('NA', 'Not applicable', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/NA');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('wMean', 'Winter Mean', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/wMean');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('3hAbove', 'Three consecutive hours in exceedance', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/3hAbove');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('90.4th', 'The percentile 90.4 for PM10', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/90.4th');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('AEI', 'Average Exposure Indicator', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/AEI');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('aMean', 'Annual mean / average', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/aMean');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('AOT40c', 'AOT40 vegetation protection', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/AOT40c');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('AOT40c-5yr', 'AOT40 vegetation protection averaged', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/AOT40c-5yr');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('AOT40f', 'AOT 40 forest protection', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/AOT40f');
INSERT INTO public.eea_reportingmetrics (id, label, uri) VALUES ('daysAbove', 'Days in exceedance in a calendar year', 'http://dd.eionet.europa.eu/vocabulary/aq/reportingmetric/daysAbove');

INSERT INTO public.eea_resultnaturevalues (id, label, notation, uri) VALUES ('primary', 'primary', 'primary', 'http://inspire.ec.europa.eu/codelist/resultnaturevalue/primary');
INSERT INTO public.eea_resultnaturevalues (id, label, notation, uri) VALUES ('processed', 'processed', 'processed', 'http://inspire.ec.europa.eu/codelist/resultnaturevalue/processed');
INSERT INTO public.eea_resultnaturevalues (id, label, notation, uri) VALUES ('simulated', 'simulated', 'simulated', 'http://inspire.ec.europa.eu/codelist/resultnaturevalue/simulated');

INSERT INTO public.eea_stationclassifications (id, label, notation, uri) VALUES ('background', 'Background', 'Background', 'http://dd.eionet.europa.eu/vocabulary/aq/stationclassification/background');
INSERT INTO public.eea_stationclassifications (id, label, notation, uri) VALUES ('industrial', 'Industrial', 'Industrial', 'http://dd.eionet.europa.eu/vocabulary/aq/stationclassification/industrial');
INSERT INTO public.eea_stationclassifications (id, label, notation, uri) VALUES ('traffic', 'Traffic', 'Traffic', 'http://dd.eionet.europa.eu/vocabulary/aq/stationclassification/traffic');

INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1', 'Sulphur dioxide (air)', 'SO2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (4, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/4', 'Total suspended particulates (aerosol)', 'SPM');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5', 'Particulate matter < 10 µm (aerosol)', 'PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7', 'Ozone (air)', 'O3');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (8, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8', 'Nitrogen dioxide (air)', 'NO2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (9, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9', 'Nitrogen oxides (air)', 'NOX as NO2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (10, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10', 'Carbon monoxide (air)', 'CO');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (11, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/11', 'Hydrogen sulphide (air)', 'H2S');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (12, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/12', 'Lead (aerosol)', 'Pb');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (13, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/13', 'Mercury (aerosol)', 'Hg');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (14, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/14', 'Cadmium (aerosol)', 'Cd');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (15, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/15', 'Nickel (aerosol)', 'Ni');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (16, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/16', 'Chromium (aerosol)', 'Cr');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (17, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/17', 'Manganese (aerosol)', 'Mn');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (18, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/18', 'Arsenic (aerosol)', 'As');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (19, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/19', 'Carbon disulphide (air)', 'CS2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (20, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/20', 'Benzene (air)', 'C6H6');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (38, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/38', 'Nitrogen monoxide (air)', 'NO');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1129, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1129', 'Benzo(a)pyrene in PM2.5 (air+aerosol)', 'BaP in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5012, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5012', 'Lead in PM10 (aerosol)', 'Pb in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5013, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5013', 'Mercury in PM10 (aerosol)', 'Hg in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5014, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5014', 'Cadmium in PM10 (aerosol)', 'Cd in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5015, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5015', 'Nickel in PM10 (aerosol)', 'Ni in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5016, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5016', 'Chromium in PM10 (aerosol)', 'Cr in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5017, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5017', 'Manganese in PM10 (aerosol)', 'Mn in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5018, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5018', 'Arsenic in PM10 (aerosol)', 'As in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5029, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5029', 'Benzo(a)pyrene in PM10 (aerosol)', 'BaP in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5045, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5045', 'Ammonium in PM10 (aerosol)', 'NH4+ in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5046, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5046', 'Nitrate in PM10 (aerosol)', 'NO3- in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5047, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5047', 'sulphate in PM10 (aerosol)', 'SO42-  in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5048, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5048', 'Selenium in PM10 (aerosol)', 'Se in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5049, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5049', 'Vanedium in PM10 (aerosol)', 'V in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5129, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5129', 'Benzo(a)pyrene in PM10 (air+aerosol)', 'BaP in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (6001, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001', 'Particulate matter < 2.5 µm (aerosol)', 'PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (6015, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6015', 'Benzo(a)pyrene (air+aerosol)', 'BaP');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (42, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/42', 'Phenol', 'C6H6O or C6H5OH');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (25, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/25', 'Formaldehyde (air)', 'HCHO');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (47, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/47', 'Particulate sulphate (aerosol)', 'SO4 (H2SO4 aerosols) (SO4--)');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (6, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6', 'Black smoke (air)', 'BS');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (21, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/21', 'Toluene (air)', 'C6H5-CH3');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (431, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/431', 'Ethyl benzene (air)', 'C6H5-C2H5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (482, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/482', 'Eo-Xylene (air)', 'o-C6H4-(CH3)2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (637, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/637', 'Dibenzo(ah)pyrene (air+aerosol)', 'Dibenzo(ah)pyrene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5610, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5610', 'Benzo(a)anthracene in PM10 (aerosol)', 'Benzo(a)anthracene in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5617, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5617', 'Benzo(b)fluoranthene in PM10 (aerosol)', 'Benzo(b)fluoranthene in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5626, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5626', 'Benzo(k)fluoranthene in PM10 (aerosol)', 'Benzo(k)fluoranthene in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5655, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5655', 'Indeno_123cd_pyrene in PM10 (aerosol)', 'Indeno-(1,2,3-cd)pyrene in PM');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5759, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5759', 'Benzo(j)fluoranthene in PM10 (aerosol)', 'Benzo(j)fluoranthene in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (4013, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/4013', 'Elemental Gaseous Mercury (air+aerosol)', 'Hg0');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (464, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/464', 'm,p-Xylene (air)', 'm,p-C6H4(CH3)2');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (5419, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5419', 'Dibenzo(ah)anthracene in PM10 (aerosol)', 'Dibenzo(ah)anthracene in PM10');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1045, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1045', 'Ammonium in PM2.5 (aerosol)', 'NH4+ in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1046, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1046', 'Nitrate in PM2.5 (aerosol)', 'NO3- in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1047, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1047', 'Sulphate in PM2.5 (aerosol)', 'SO42- in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1629, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1629', 'Calcium in PM2.5 (aerosol)', 'Ca2+ in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1631, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1631', 'Chloride in PM2.5 (aerosol)', 'Cl- in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1657, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1657', 'Potassium in PM2.5 (aerosol)', 'K+ in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1659, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1659', 'Magnesium in PM2.5 (aerosol)', 'Mg2+ in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1668, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1668', 'Sodium in PM2.5 (aerosol)', 'Na+ in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1771, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1771', 'Elemental carbon in PM2.5 (aerosol)', 'EC in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (1772, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1772', 'Organic carbon in PM2.5 (aerosol)', 'OC in PM2.5');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7015, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7015', 'Nickel (precip+dry_dep)', 'Ni');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7018, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7018', 'Arsenic (precip+dry_dep)', 'As');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7014, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7014', 'Cadmium (precip+dry_dep)', 'Cd');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7012, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7012', 'Lead (precip+dry_dep)', 'Pb');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7029, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7029', 'Benzo(a)pyrene (precip+dry_dep)', 'BaP');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (611, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/611', 'Benzo(a)anthracene (precip+dry_dep)', 'Benzo(a)anthracene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (618, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/618', 'Benzo(b)fluoranthene (precip+dry_dep)', 'Benzo(b)fluoranthene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (760, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/760', 'Benzo(j)fluoranthene (precip+dry_dep)', 'Benzo(j)fluoranthene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (627, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/627', 'Benzo(k)fluoranthene (precip+dry_dep)', 'Benzo(k)fluoranthene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (656, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/656', 'indeno_123cd_pyrene (precip+dry_dep)', 'Indeno-(1,2,3-cd)pyrene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7419, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7419', 'Dibenzo(ah)anthracene (precip+dry_dep)', 'Dibenzo(ah)anthracene');
INSERT INTO public.eea_pollutants (id, uri, label, notation) VALUES (7013, 'http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7013', 'Mercury (precip+dry_dep)', 'Hg');

INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('month', 'Month', 'month', 1, 'http://dd.eionet.europa.eu/vocabulary/uom/time/month');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('variable', 'Variable', 'variable', 1, 'http://dd.eionet.europa.eu/vocabulary/uom/time/variable');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('second', 'Second', 's', 1, 'http://dd.eionet.europa.eu/vocabulary/uom/time/second');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('var', 'Variable', 'variable', 1, 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/var');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('other', 'Other', 'other', 1, 'http://dd.eionet.europa.eu/vocabulary/uom/time/other');
-- dropped (duplicate of aq/primaryObservation): http://dd.eionet.europa.eu/vocabulary/uom/time/day
-- dropped (duplicate of aq/primaryObservation): http://dd.eionet.europa.eu/vocabulary/uom/time/week
-- dropped (duplicate of aq/primaryObservation): http://dd.eionet.europa.eu/vocabulary/uom/time/hour
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('hour', 'Hour', 'h', 3600, 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/hour');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('day', 'Day', 'd', 86400, 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/day');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('year', 'Year', 'y or a', 31536000, 'http://dd.eionet.europa.eu/vocabulary/uom/time/year');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('minute', 'Minute', 'm', 60, 'http://dd.eionet.europa.eu/vocabulary/uom/time/minute');
INSERT INTO public.eea_times (id, label, notation, timestep, uri) VALUES ('week', 'Weekly average/mean', 'week', 604800, 'http://dd.eionet.europa.eu/vocabulary/aq/primaryObservation/week');

INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC', 'Coordinated Universal Time', 'UTC', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+01', 'UTC+01', 'UTC+01', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+01');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+02', 'UTC+02', 'UTC+02', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+02');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+03', 'UTC+03', 'UTC+03', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+03');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+04', 'UTC+04', 'UTC+04', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+04');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+05', 'UTC+05', 'UTC+05', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+05');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC+06', 'UTC+06', 'UTC+06', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC+06');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-01', 'UTC-01', 'UTC-01', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-01');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-02', 'UTC-02', 'UTC-02', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-02');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-03', 'UTC-03', 'UTC-03', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-03');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-04', 'UTC-04', 'UTC-04', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-04');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-05', 'UTC-05', 'UTC-05', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-05');
INSERT INTO public.eea_timezones (id, label, notation, uri) VALUES ('UTC-06', 'UTC-06', 'UTC-06', 'http://dd.eionet.europa.eu/vocabulary/aq/timezone/UTC-06');

INSERT INTO public.eea_zonetypes (id, label, uri) VALUES ('agg', 'Agglomeration', 'http://dd.eionet.europa.eu/vocabulary/aq/zonetype/agg');
INSERT INTO public.eea_zonetypes (id, label, uri) VALUES ('noagg', 'Non-agglomeration', 'http://dd.eionet.europa.eu/vocabulary/aq/zonetype/noagg');

INSERT INTO public.settings (country_code_id, timezone_id) VALUES (NULL, NULL);
-- ===========================================================================
-- AQR3 OMR_08 Validity / OMR_09 Verification
--
-- The only two codelists whose full value sets are documented in this repo (see
-- the comments on observations.observationvalidity_id / observationverification_id
-- in schema.sql), so they can be seeded here safely.
-- ===========================================================================
INSERT INTO public.eea_observationvalidity (id, label, notation, uri) VALUES
  (-99, 'Not valid due to station maintenance or calibration', '-99', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/-99'),
  (-1,  'Not valid', '-1', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/-1'),
  (1,   'Valid', '1', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/1'),
  (2,   'Valid, below detection limit', '2', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/2'),
  (3,   'Valid, below detection limit and value substituted', '3', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/3'),
  (4,   'Valid, ozone CCQM comparison', '4', 'http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity/4');

INSERT INTO public.eea_observationverification (id, label, notation, uri) VALUES
  (1, 'Verified', '1', 'http://dd.eionet.europa.eu/vocabulary/aq/observationverification/1'),
  (2, 'Preliminary verified', '2', 'http://dd.eionet.europa.eu/vocabulary/aq/observationverification/2'),
  (3, 'Not verified', '3', 'http://dd.eionet.europa.eu/vocabulary/aq/observationverification/3');

-- ===========================================================================
-- STILL UNSEEDED — fetch from the EEA Data Dictionary before reporting
--
-- These codelists have no rows here and no authoritative source inside this
-- repo, so they are deliberately left empty rather than filled with guessed
-- values: a wrong EEA code fails Reportnet3 QC in a confusing way, whereas an
-- empty column is obviously incomplete.
--
--   eea_countries                 CountryCode on every table; settings.country_code_id
--   eea_aggregationprocess        MOE_03 / MRI_04 / CAM_04 DataAggregationProcessId
--   eea_analyticaltechnique       SPP_10 AnalyticalTechnique
--   eea_authorityobject           AUT_03 AuthorityRole
--   eea_authorityinstance         AUT_05 AuthorityInstance
--   eea_authoritystatus           AUT_10 AuthorityStatus
--   eea_spocategory               SPL_06 SamplingPointCategory
--   eea_zonecategory              ARZ_06 ZoneCategory
--   eea_objectivetypes            ARZ_11 ObjectiveType
--   eea_datatable                 DOC_02 DataTable
--   eea_documentobject            DOC_03 DocumentType
--   eea_environmentalobjective    used by assessmentregime_zones
--
-- Populate with raven-rn3-db/populate_lookups_v4_2.py (fetches from
-- dd.eionet.europa.eu), then set settings.country_code_id to the reporting
-- country — CountryCode is the first column of all 17 AQR3 tables and stays
-- blank until it is set.
-- ===========================================================================

-- ===========================================================================
-- AQR3 ARZ_11 ObjectiveType
--
-- assessment_regimes.objective_type_id has its FK to eea_objectivetypes, which is
-- what the ARZ export and plans_programs_export.py join to. Only the similarly
-- named eea_objecttypes was seeded, so ObjectiveType came out blank in the CSV.
-- Both are seeded from the same aq/objectivetype vocabulary; eea_objecttypes is
-- retained because the XML export and the objecttypes lookup endpoint use it.
-- ===========================================================================
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('ALT', 'Alert threshold (ALT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ALT');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('CL', 'Critical level (CL)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/CL');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('ECO', 'Exposure concentration obligation (ECO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ECO');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('ERT', 'Exposure reduction target (ERT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/ERT');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('INT', 'Information Threshold (INT)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/INT');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('LTO', 'Long term objective (LTO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LTO');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('LV', 'Limit Value (LV)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LV');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('LVmaxMOT', 'Limit value plus maximum margin of', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LVmaxMOT');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('LVMOT', 'Limit value plus applicable margin of', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LVMOT');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('MO', 'Monitoring objective (MO)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/MO');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('TV', 'Target Value (TV)', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/TV');
INSERT INTO public.eea_objectivetypes (id, label, uri) VALUES ('LV-S2', 'Limit Value (Stage II) for reporting PM2.5 only', 'http://dd.eionet.europa.eu/vocabulary/aq/objectivetype/LV-S2');

-- ===========================================================================
-- Normalise notation
--
-- The v4 convention is id = notation for codelist tables (the id *is* the short
-- EEA code; `uri` holds the full URI). Several of the seeds above predate that and
-- supply only (id, label, uri), leaving notation NULL.
--
-- That matters because every AQR3 CSV reads `eea_*.notation` — a NULL notation
-- produces a blank column even though the table has rows. It is exactly why
-- AssessmentRegimeZone reported empty ZoneType, ProtectionTarget, ObjectiveType,
-- ReportingMetric and AssessmentThresholdExceedance.
--
-- Applied generically rather than row by row so a future seed cannot reintroduce it.
-- populate_vocabularies.py sets notation explicitly, so this only fills the gap for
-- offline installs.
-- ===========================================================================
DO $$
    DECLARE
        t text;
        n integer;
    BEGIN
        FOR t IN
            SELECT c.table_name
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
              AND c.table_name LIKE 'eea\_%'
              AND c.column_name = 'notation'
            ORDER BY c.table_name
            LOOP
                EXECUTE format(
                    'UPDATE %I SET notation = id::text WHERE notation IS NULL OR notation = %L',
                    t, '');
                GET DIAGNOSTICS n = ROW_COUNT;
                IF n > 0 THEN
                    RAISE NOTICE 'notation backfilled from id: % (% rows)', t, n;
                END IF;
            END LOOP;
    END
$$;
