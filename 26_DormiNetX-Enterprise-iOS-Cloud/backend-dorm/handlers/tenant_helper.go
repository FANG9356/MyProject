package handlers

import (
	"database/sql"
	"fmt"
	"net/http"
)


func getTenantDB(r *http.Request, fallback *sql.DB) *sql.DB {
	tenant, err := RequestTenantDB(r, fallback)
	if err == nil {
		return tenant
	}
	return fallback
}


func RequestTenantDB(r *http.Request, master *sql.DB) (*sql.DB, error) {
	adminID := r.Context().Value("admin_id")
	if adminID != nil {
		if id, ok := adminID.(int); ok {
			var superadminID int

			err := master.QueryRow(`
				SELECT s.id
				FROM admins a
				JOIN admins s ON a.email = s.email
				WHERE a.id = ? AND s.role = 'superadmin'
				LIMIT 1
			`, id).Scan(&superadminID)

			if err != nil || superadminID <= 0 {
				return nil, fmt.Errorf("resolve tenant owner: %w", err)
			}

			return GetTenantDB(superadminID)
		}
	}
	return nil, fmt.Errorf("missing authenticated admin id")
}
