export { useRolesList, useRoleDetail, useAvailablePermissions, useRoleUsers, useCreateRole, useUpdateRole, useDeleteRole, useSetPermissions, useAssignUsers, useRemoveUsers, useRoleAuditLog } from './hooks/use-roles';
export { rolesApi } from './api';
export type { Role, RoleDetail, Permission, RoleUser, RoleFilters } from './types';
export * from './components';