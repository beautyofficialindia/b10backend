# ADMIN_WORKFLOW.md

## System Navigation for B10 IT Solution Staff

The internal CRM operates primarily via automated workflows, but Sales and Admin staff must interface with it to move leads across the finish line.

### 1. Lead Qualification Pipeline
When a user chats with the AI, their information is extracted passively.
- **Gathering**: The lead is missing required fields (e.g., Email or Industry).
- **Qualified**: The system successfully extracted all required fields. **An email notification is automatically dispatched to the Sales team.**

### 2. Modifying Lead Status
Sales Agents can log into the system and patch a Lead's status to `converted`, `lost`, or `escalated` using `PATCH /api/v1/admin/leads/<id>/`. 
- **Analytics Sync**: Moving a lead to `converted` automatically triggers an event in the Analytics subsystem to update the conversion funnel.

### 3. CRM Follow-ups
If a Lead requires a manual email or phone call, Sales agents generate a `LeadFollowUp` record attached to the Lead. 
- These appear on the `CRMDashboardAPIView`.
- Once the call is completed, the agent marks the follow-up as `completed`, which automatically generates a permanent `LeadActivity` log in the Lead's history.
