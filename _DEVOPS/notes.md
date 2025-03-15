# Conceptual Library notes on DevOps


### scripts commands
```shell
.\_DEVOPS\SCRIPTS\get_snapshot.ps1 "C:\GitStorage\ConceptualLibrary" "frontend" "frontend_snapshot"
.\_DEVOPS\SCRIPTS\get_snapshot.ps1 "C:\GitStorage\ConceptualLibrary" "backend" "backend_snapshot"
.\_DEVOPS\SCRIPTS\get_snapshot.ps1 "C:\GitStorage\ConceptualLibrary" "database" "database_snapshot"
.\_DEVOPS\SCRIPTS\get_snapshot.ps1 "C:\GitStorage\ConceptualLibrary" "." "full_codebase" 
# note, the full_code base will get you a file so big that any llm wont be able to use it, but might be nice to have for other purposes - sjd
```

```shell
# these are how you interact with the docker containers
.\_DEVOPS\SCRIPTS\full_restart_docker.ps1
.\_DEVOPS\SCRIPTS\restart_docker.ps1
```