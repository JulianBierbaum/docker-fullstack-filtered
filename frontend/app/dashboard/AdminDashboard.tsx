'use client'

import { useEffect, useState } from 'react'
import api from '@/app/api'
import { Input } from '@/components/ui/input'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog"
import { Button } from '@/components/ui/button'
import { Label } from "@/components/ui/label"
import { DataTable, eventColumns, Event } from "./dataTable"
import { useAuth } from '@/app/hooks/useAuth'

const defaultEvent: Partial<Event> = {
    title: '',
    event_date: new Date().toISOString().split('T')[0],
    start_time: '12:00:00',
    description: '',
    ticket_capacity: 100,
    location_id: 1,
}

export default function AdminDashboard() {
    const { logout } = useAuth()
    const [events, setEvents] = useState<Event[]>([])
    const [locationNames, setLocationNames] = useState<Record<number, string>>({})
    const [organizerNames, setOrganizerNames] = useState<Record<number, string>>({})
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')

    const [selectedEvent, setSelectedEvent] = useState<Partial<Event>>()
    const [open, setOpen] = useState(false)

    const fetchEvents = async () => {
        try {
            const { data: eventsData } = await api.get<Event[]>('/events/')
            setEvents(eventsData)

            const locationIds = Array.from(new Set(eventsData.map((e) => e.location_id)))
            const organizerIds = Array.from(new Set(eventsData.map((e) => e.organizer_id)))

            const locationPromises = locationIds.map((id) =>
                api.get(`/locations/${id}`).then((res) => ({ id, name: res.data.name })).catch(() => ({ id, name: `Location ${id}` }))
            )
            const organizerPromises = organizerIds.map((id) =>
                api.get(`/users/${id}`).then((res) => ({ id, name: res.data.username })).catch(() => ({ id, name: `User ${id}` }))
            )

            const locations = await Promise.all(locationPromises)
            const organizers = await Promise.all(organizerPromises)

            const locMap: Record<number, string> = {}
            locations.forEach((l) => (locMap[l.id] = l.name))
            setLocationNames(locMap)

            const orgMap: Record<number, string> = {}
            organizers.forEach((o) => (orgMap[o.id] = o.name))
            setOrganizerNames(orgMap)
        } catch (error) {
            console.error('Error fetching data:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchEvents()
    }, [])

    const openDialog = (event: Event) => {
        setSelectedEvent({ ...event })
        setOpen(true)
    }

    const openNewDialog = () => {
        setSelectedEvent({ ...defaultEvent })
        setOpen(true)
    }

    const handleSave = async () => {
        if (!selectedEvent) return
        const isUpdating = selectedEvent.id !== undefined

        try {
            if (isUpdating) {
                const { id, ...data } = selectedEvent
                await api.put(`/events/${id}`, data)
                setEvents((prev) =>
                    prev.map((e) => (e.id === id ? { ...selectedEvent } as Event : e))
                )
            } else {
                const { data: newEvent } = await api.post<Event>('/events/', selectedEvent)
                setEvents((prev) => [newEvent, ...prev])
            }
            setOpen(false)
        } catch (error) {
            console.error('Failed to save event:', error)
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this event?')) return
        try {
            await api.delete(`/events/${id}`)
            setEvents((prev) => prev.filter((e) => e.id !== id))
        } catch (error) {
            console.error('Failed to delete event:', error)
        }
    }

    const filteredEvents = events.filter((item) =>
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        (item.description || '').toLowerCase().includes(search.toLowerCase()) ||
        (locationNames[item.location_id] || '').toLowerCase().includes(search.toLowerCase())
    )

    const isUpdating = selectedEvent?.id !== undefined
    const columns = eventColumns(openDialog, handleDelete)

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-end items-center">
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
                <Button onClick={openNewDialog}>Create New Event</Button>
            </div>

            <DataTable columns={columns} data={filteredEvents} onRowClick={openDialog} />

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent onInteractOutside={(e) => e.preventDefault()}>
                    <DialogHeader>
                        <DialogTitle>{isUpdating ? 'Edit Event' : 'Create New Event'}</DialogTitle>
                    </DialogHeader>

                    {selectedEvent && (
                        <div className="space-y-4 mt-4">
                            <div className="space-y-2">
                                <Label>Title</Label>
                                <Input
                                    value={selectedEvent.title || ''}
                                    onChange={(e) =>
                                        setSelectedEvent({ ...selectedEvent, title: e.target.value })
                                    }
                                    placeholder="Event Title"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Date</Label>
                                    <Input
                                        type="date"
                                        value={selectedEvent.event_date || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, event_date: e.target.value })
                                        }
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Time</Label>
                                    <Input
                                        type="time"
                                        step="1"
                                        value={selectedEvent.start_time || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, start_time: e.target.value })
                                        }
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Description</Label>
                                <Input
                                    value={selectedEvent.description || ''}
                                    onChange={(e) =>
                                        setSelectedEvent({ ...selectedEvent, description: e.target.value })
                                    }
                                    placeholder="Event Description"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Location ID</Label>
                                    <Input
                                        type="number"
                                        value={selectedEvent.location_id || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, location_id: parseInt(e.target.value) })
                                        }
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Capacity</Label>
                                    <Input
                                        type="number"
                                        value={selectedEvent.ticket_capacity || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, ticket_capacity: parseInt(e.target.value) })
                                        }
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    <DialogFooter className="mt-4">
                        <Button variant="outline" onClick={() => setOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
