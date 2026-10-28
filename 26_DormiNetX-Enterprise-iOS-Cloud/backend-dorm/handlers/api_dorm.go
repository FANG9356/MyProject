package handlers

import (
	"database/sql"
)


func SetupDormRoutes(master, db *sql.DB) {
	SetupDashboardRoutes(db)
	SetupLogRoutes(db)
	SetupPaymentRoutes(db)
	SetupRoomRoutes(db)
	SetupUserRoutes(db)
	SetupMaintenanceRoutes(master, db)
	SetupSyncRoutes(db)
}

