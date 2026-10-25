package handlers

import (
	"database/sql"
)

func SetupDormRoutes(db *sql.DB) {
	SetupDashboardRoutes(db)
	SetupLogRoutes(db)
	SetupPaymentRoutes(db)
	SetupRoomRoutes(db)
	SetupUserRoutes(db)
	SetupMaintenanceRoutes(db)
}
