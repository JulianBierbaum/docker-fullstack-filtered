'use client'

import { Button } from '@/components/ui/button'
import { useAuth } from '@/app/hooks/useAuth'

export default function UserDashboard() {
    const { logout } = useAuth()

    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <div className="absolute top-6 right-6">
                <Button onClick={logout} variant="outline">
                    Logout
                </Button>
            </div>
            <p className="text-xl">user page</p>
        </div>
    )
}
