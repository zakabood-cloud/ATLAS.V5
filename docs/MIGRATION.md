# Legacy project migration and recovery

Migration is an explicit, local schema change. It does not import, replace or certify prior evidence. Stop every writer and external worker first.

## Before migrating schema 1

1. Inspect `python3 -m atlas status PROJECT_ID` and validate the event chain and artifacts.
2. Stop all ATLAS processes and confirm the project is quiesced. Reconcile any running/remote work through the actual client; never assume a timeout stopped it.
3. Make and retain a full project-directory backup, including files and database. ATLAS backups are unencrypted; protect them accordingly.
4. Obtain actual user authorization to migrate. Do not infer consent from installing v4.

Then run:

```sh
python3 -m atlas migrate PROJECT_ID \
  --backup PATH/TO/QUIESCED-BACKUP.zip \
  --authorization 'ACTUAL USER INSTRUCTION' \
  --quiesced
```

Replace the example path and authorization with actual values. Migration creates a checked full backup before updating the state database. It records the previous state, authorization and backup receipt; preserves existing project files, but moves an active project back to MANDATE (or leaves an INTAKE project in INTAKE), removes old task records, and retains only the mandate seal. It does not translate old plans, attestations or tool state.

After migration, revisit intake/mandate where needed, then create a fresh observable `enablement.json` and topic-specific `access_plan.json`. Obtain current user choices and real access tests before META. Rebuild the schema-2 protocol and re-review every claim/source snapshot/calculation. Legacy evidence may remain as source material but is not schema-2 reviewed evidence; create updated records with claim/snapshot-bound assessments and a final review bound to the current evidence register. Recreate readiness and orchestration files, then advance only through sequential passing gates. See [schemas](SCHEMAS.md) and [access](ACCESS.md).

If validation fails, stop and investigate; do not edit the database, event hashes or receipts to force a transition. Preserve the pre-migration backup.

## Checkpoint restore is a recovery hold

`restore PROJECT_ID checkpoints/state-....sqlite3` restores a checked database checkpoint and quarantines the current database, but **now leaves a recovery hold unless the restored checkpoint already had a hold**. This prevents a restore to older state from silently clearing a later access block or other interruption. Inspect the restored status, surviving files, known later blocks and remote jobs; reconcile what may have happened after the checkpoint with the user. For schema 2, obtain explicit authorization and resume only when the recovery scope is understood:

```sh
python3 -m atlas resume PROJECT_ID \
  --reason 'Reconciled restored state and authorized continuation' \
  --authorization 'ACTUAL USER INSTRUCTION'
```

This ordinary recovery hold is not a retry authorization for a lost/blocked access event. If access remains unresolved, record or restore the accurate block and follow the scoped access workflow; do not resume research. A checkpoint restore is database-only: artifacts may have changed or been lost and must be checked against restored seals. Concurrent restore/writers are unsupported.

## Full project archive restore

`project-restore` verifies an archive and copies project bytes only into a nonexistent target directory. It does not authenticate connections, refresh expired receipts, prove current capability availability, or grant authorization to continue. Treat it as restored data; inspect status and independently revalidate access and all artifacts before work.
