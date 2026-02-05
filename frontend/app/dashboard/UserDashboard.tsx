'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import api from '@/app/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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

interface Event {
    id: number
    title: string
    description: string | null
    event_date: string
    start_time: string
    location_id: number
    ticket_capacity: number
}

export default function UserDashboard() {
    const { logout } = useAuth()
    const [events, setEvents] = useState<Event[]>([])
    const [availableTickets, setAvailableTickets] = useState<Record<number, number>>({})
    const [search, setSearch] = useState('')
    const [loading, setLoading] = useState(true)
    const [purchasing, setPurchasing] = useState<number | null>(null)

    // Dialog state
    const [dialogOpen, setDialogOpen] = useState(false)
    const [dialogMessage, setDialogMessage] = useState('')
    const [dialogType, setDialogType] = useState<'success' | 'error'>('success')

    const fetchEvents = async () => {
        try {
            const { data } = await api.get('/events/')
            setEvents(data)

            const ticketCounts: Record<number, number> = {}
            await Promise.all(
                data.map(async (event: Event) => {
                    try {
                        const { data: count } = await api.get(`/tickets/event/${event.id}/available/count`)
                        ticketCounts[event.id] = count
                    } catch {
                        ticketCounts[event.id] = 0
                    }
                })
            )
            setAvailableTickets(ticketCounts)
        } catch (error) {
            console.error('Error fetching events:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchEvents()
    }, [])

    const showDialog = (message: string, type: 'success' | 'error') => {
        setDialogMessage(message)
        setDialogType(type)
        setDialogOpen(true)
    }

    const handleBuy = async (eventId: number) => {
        setPurchasing(eventId)
        try {
            await api.post(`/bookings/event/${eventId}`)
            showDialog('Success! Your ticket is confirmed.', 'success')
            fetchEvents()
        } catch (error: unknown) {
            const err = error as { response?: { data?: { detail?: string } } }
            showDialog(err.response?.data?.detail || 'Error during purchase.', 'error')
        } finally {
            setPurchasing(null)
        }
    }

    const filteredEvents = events.filter(e =>
        e.title.toLowerCase().includes(search.toLowerCase()) ||
        (e.description || '').toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-end items-center gap-4">
                <Link href="/dashboard/tickets">
                    <Button variant="outline">My Tickets</Button>
                </Link>
                <Button onClick={logout} variant="outline">
                    Logout
                </Button>
            </div>

            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Events</h1>
            </div>

            <div className="flex justify-between items-center gap-4">
                <Input
                    placeholder="Search Events..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="max-w-xl"
                />
            </div>

            {loading ? (
                <div className="text-center py-4">Loading...</div>
            ) : filteredEvents.length === 0 ? (
                <div className="text-center py-4 text-muted-foreground">No events found.</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredEvents.map((event) => {
                        const available = availableTickets[event.id] ?? 0
                        return (
                            <Card key={event.id}>
                                <CardHeader>
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="text-lg">{event.title}</CardTitle>
                                        <Badge variant={available > 0 ? "secondary" : "destructive"}>
                                            {available > 0 ? `${available} left` : "Sold Out"}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    <p className="text-sm text-muted-foreground">
                                        {event.description || 'No description'}
                                    </p>
                                    <div className="text-sm">
                                        <p>Date: {event.event_date}</p>
                                        <p>Time: {event.start_time}</p>
                                        <p>Location ID: {event.location_id}</p>
                                    </div>
                                </CardContent>
                                <CardFooter>
                                    <Button
                                        className="w-full"
                                        disabled={available <= 0 || purchasing === event.id}
                                        onClick={() => handleBuy(event.id)}
                                    >
                                        {purchasing === event.id ? 'Buying...' : 'Buy Ticket'}
                                    </Button>
                                </CardFooter>
                            </Card>
                        )
                    })}
                </div>
            )}

            {/* Result Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{dialogType === 'success' ? 'Success' : 'Error'}</DialogTitle>
                    </DialogHeader>
                    <p>{dialogMessage}</p>
                    <DialogFooter>
                        <Button onClick={() => setDialogOpen(false)}>OK</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
