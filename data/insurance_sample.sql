-- Insurance Regulatory Compliance Query using Salesforce Data
-- This query analyzes policy cancellations and claims denials for state regulatory reporting

SELECT 
    p.Policy_Number__c,
    p.Policy_Type__c,
    p.Effective_Date__c,
    p.Expiration_Date__c,
    p.Premium_Amount__c,
    p.Payment_Frequency__c,
    a.Account_ID__c,
    a.First_Name__c,
    a.Last_Name__c,
    a.SSN__c,
    a.Date_of_Birth__c,
    a.Email__c,
    a.Phone__c,
    a.Mailing_Address__c,
    a.Mailing_City__c,
    a.Mailing_State__c,
    a.Mailing_Zip__c,
    a.Risk_Score__c,
    c.Claim_Number__c,
    c.Date_of_Loss__c,
    c.Claim_Amount__c,
    c.Claim_Status__c,
    c.Denial_Reason__c,
    c.Denial_Date__c,
    c.Adjuster_ID__c,
    c.Coverage_Type__c,
    cn.Cancellation_Reason__c,
    cn.Cancellation_Date__c,
    cn.Refund_Amount__c,
    cn.Notice_Date__c,
    cn.Days_Notice__c
FROM 
    Insurance_Policy__c p
INNER JOIN 
    Account a ON p.Account_ID__c = a.Account_ID__c
LEFT JOIN 
    Claim__c c ON p.Policy_Number__c = c.Policy_Number__c
LEFT JOIN 
    Cancellation__c cn ON p.Policy_Number__c = cn.Policy_Number__c
WHERE 
    (c.Claim_Status__c = 'Denied' OR cn.Cancellation_Reason__c IS NOT NULL)
    AND p.Effective_Date__c >= '2024-01-01'
    AND p.Effective_Date__c <= '2024-03-15'
    AND a.Mailing_State__c = 'NY'
    AND p.Policy_Type__c IN ('Auto', 'Homeowners', 'Renters')
    AND (
        (c.Denial_Reason__c IS NOT NULL AND DATEDIFF(day, c.Date_of_Loss__c, c.Denial_Date__c) < 30)
        OR 
        (cn.Cancellation_Reason__c IS NOT NULL AND cn.Days_Notice__c < 45)
    )
GROUP BY
    p.Policy_Number__c,
    p.Policy_Type__c,
    p.Effective_Date__c,
    p.Expiration_Date__c,
    p.Premium_Amount__c,
    p.Payment_Frequency__c,
    a.Account_ID__c,
    a.First_Name__c,
    a.Last_Name__c,
    a.SSN__c,
    a.Date_of_Birth__c,
    a.Email__c,
    a.Phone__c,
    a.Mailing_Address__c,
    a.Mailing_City__c,
    a.Mailing_State__c,
    a.Mailing_Zip__c,
    a.Risk_Score__c,
    c.Claim_Number__c,
    c.Date_of_Loss__c,
    c.Claim_Amount__c,
    c.Claim_Status__c,
    c.Denial_Reason__c,
    c.Denial_Date__c,
    c.Adjuster_ID__c,
    c.Coverage_Type__c,
    cn.Cancellation_Reason__c,
    cn.Cancellation_Date__c,
    cn.Refund_Amount__c,
    cn.Notice_Date__c,
    cn.Days_Notice__c
HAVING 
    COUNT(c.Claim_Number__c) > 0 OR COUNT(cn.Cancellation_Date__c) > 0
ORDER BY 
    a.Risk_Score__c DESC,
    p.Premium_Amount__c DESC
LIMIT 500;