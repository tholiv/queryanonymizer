-- Healthcare Industry SQL Query for Salesforce Data
-- This query analyzes patient engagement, appointment attendance, and medication adherence

SELECT 
    p.Patient_ID__c,
    p.First_Name__c,
    p.Last_Name__c,
    p.Date_of_Birth__c,
    p.Insurance_Provider__c,
    p.Insurance_Policy_Number__c,
    p.Email__c,
    p.Phone__c,
    p.Primary_Care_Physician__c,
    COUNT(a.Id) AS Total_Appointments,
    SUM(CASE WHEN a.Status__c = 'Completed' THEN 1 ELSE 0 END) AS Completed_Appointments,
    SUM(CASE WHEN a.Status__c = 'No-Show' THEN 1 ELSE 0 END) AS Missed_Appointments,
    AVG(s.Patient_Satisfaction_Score__c) AS Average_Satisfaction,
    COUNT(DISTINCT m.Medication_Name__c) AS Unique_Medications,
    MAX(m.Last_Refill_Date__c) AS Most_Recent_Refill,
    DATEDIFF(day, MAX(m.Last_Refill_Date__c), CURRENT_DATE) AS Days_Since_Last_Refill
FROM 
    Patient__c p
LEFT JOIN 
    Appointment__c a ON p.Patient_ID__c = a.Patient_ID__c
LEFT JOIN 
    Satisfaction_Survey__c s ON a.Id = s.Appointment_ID__c
LEFT JOIN 
    Medication__c m ON p.Patient_ID__c = m.Patient_ID__c
WHERE 
    p.Enrollment_Date__c >= '2023-01-01'
    AND p.Clinic_Location__c = 'North Memorial Health Clinic'
    AND p.Insurance_Provider__c IN ('Blue Cross Blue Shield', 'Medicare', 'Aetna')
    AND NOT EXISTS (
        SELECT 1 
        FROM Patient_Opt_Out__c o 
        WHERE o.Patient_ID__c = p.Patient_ID__c 
        AND o.Opt_Out_Type__c = 'Data Analysis'
    )
GROUP BY 
    p.Patient_ID__c,
    p.First_Name__c,
    p.Last_Name__c,
    p.Date_of_Birth__c,
    p.Insurance_Provider__c,
    p.Insurance_Policy_Number__c,
    p.Email__c,
    p.Phone__c,
    p.Primary_Care_Physician__c
HAVING 
    COUNT(a.Id) > 3
    AND AVG(s.Patient_Satisfaction_Score__c) < 4.0
ORDER BY 
    Missed_Appointments DESC,
    Days_Since_Last_Refill DESC
LIMIT 100;