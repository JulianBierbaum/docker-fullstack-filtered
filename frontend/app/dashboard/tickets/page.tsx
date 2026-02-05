'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import api from '@/app/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog"
import { useAuth } from '@/app/hooks/useAuth'
import ProtectedRoute from '@/app/protectedRoute'

interface Booking {
    booking_number: number
    user_id: number
    ticket_id: number
    created_at: string
}

export default function TicketsPage() {
    const { logout } = useAuth()
    const [bookings, setBookings] = useState<Booking[]>([])
    const [loading, setLoading] = useState(true)

    // Confirm dialog state
    const [confirmOpen, setConfirmOpen] = useState(false)
    const [bookingToCancel, setBookingToCancel] = useState<number | null>(null)

    // Result dialog state
    const [resultOpen, setResultOpen] = useState(false)
    const [resultMessage, setResultMessage] = useState('')
    const [resultType, setResultType] = useState<'success' | 'error'>('success')

    const fetchMyBookings = async () => {
        try {
            const { data } = await api.get('/bookings/me')
            setBookings(data)
        } catch (error) {
            console.error('Error fetching bookings:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchMyBookings()
    }, [])

    const openConfirmDialog = (bookingNumber: number) => {
        setBookingToCancel(bookingNumber)
        setConfirmOpen(true)
    }

    const handleCancelBooking = async () => {
        if (bookingToCancel === null) return
        setConfirmOpen(false)

        try {
            await api.delete(`/bookings/me/${bookingToCancel}`)
            setResultMessage('Booking cancelled successfully')
            setResultType('success')
            setResultOpen(true)
            fetchMyBookings()
        } catch (error: unknown) {
            const err = error as { response?: { data?: { detail?: string } } }
            setResultMessage(err.response?.data?.detail || 'Error cancelling booking')
            setResultType('error')
            setResultOpen(true)
        } finally {
            setBookingToCancel(null)
        }
    }

    return (
        <ProtectedRoute>
            <div className="p-6 space-y-6">
                <div className="flex justify-end items-center gap-4">
                    <Link href="/dashboard">
                        <Button variant="outline">Back to Events</Button>
                    </Link>
                    <Button onClick={logout} variant="outline">
                        Logout
                    </Button>
                </div>

                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold">My Tickets</h1>
                    <span className="text-muted-foreground">{bookings.length} booking(s)</span>
                </div>

                {loading ? (
                    <div className="text-center py-4">Loading...</div>
                ) : bookings.length === 0 ? (
                    <div className="text-center py-4 text-muted-foreground">
                        No bookings found. <Link href="/dashboard" className="underline">Browse events</Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {bookings.map((booking) => (
                            <Card key={booking.booking_number}>
                                <CardHeader>
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-lg">Booking #{booking.booking_number}</CardTitle>
                                        <Badge variant="secondary">Confirmed</Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    <div className="text-sm">
                                        <p>Ticket ID: {booking.ticket_id}</p>
                                        <p>Purchased: {new Date(booking.created_at).toLocaleDateString()}</p>
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button
                                        variant="destructive"
                                        className="w-full"
                                        onClick={() => openConfirmDialog(booking.booking_number)}
                                    >
                                        Cancel Booking
                                    </Button>
                                </CardFooter>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Confirm Cancel Dialog */}
                <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Cancel Booking</DialogTitle>
                        </DialogHeader>
                        <p>Are you sure you want to cancel this booking?</p>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setConfirmOpen(false)}>No</Button>
                            <Button variant="destructive" onClick={handleCancelBooking}>Yes, Cancel</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>

                {/* Result Dialog */}
                <Dialog open={resultOpen} onOpenChange={setResultOpen}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>{resultType === 'success' ? 'Success' : 'Error'}</DialogTitle>
                        </DialogHeader>
                        <p>{resultMessage}</p>
                        <DialogFooter>
                            <Button onClick={() => setResultOpen(false)}>OK</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </ProtectedRoute>
    )
}
