'use client'

import ProtectedRoute from "@/app/protectedRoute"
import { useAuth } from "@/app/hooks/useAuth"
import AdminDashboard from "./AdminDashboard"
import UserDashboard from "./UserDashboard"

export default function DashboardPage() {
    const { isVisitor } = useAuth()

    return (
        <ProtectedRoute>
            {isVisitor ? <UserDashboard /> : <AdminDashboard />}
        </ProtectedRoute>
    )
}
