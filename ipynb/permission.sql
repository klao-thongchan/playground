
WITH UserPermission AS (
    SELECT UserName, PermissionName
    FROM PermissionAssignment b
    INNER JOIN UserRoleAssignment a ON b.UserRoleId = a.UserRoleId
)

WITH fm AS (
    SELECT COUNTA(DISTINCT PermissionName)
    FROM UserPermission
    WHERE UserName = 'Frazer Macfariane'
)

WITH mc AS (
    SELECT COUNTA(DISTINCT PermissionName)
    FROM UserPermission
    WHERE UserName = 'Marina Clarke'
)

WITH nr AS (
    SELECT COUNTA(DISTINCT PermissionName)
    FROM UserPermission
    WHERE UserName = 'Nimra Rigby'
)

SELECT UPPER(Name) AS RoleName, Description AS RoleDescription, fm AS 'Frazer Macfariane', mc AS 'Marina Clarke', nr AS 'Nimra Rigby'
FROM UserRole
GROUP BY RoleName