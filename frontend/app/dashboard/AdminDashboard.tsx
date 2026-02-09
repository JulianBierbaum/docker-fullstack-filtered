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
import { DataTable, eventColumns, locationColumns, userColumns, Event, Location, User } from "./dataTable"
import { useAuth } from '@/app/hooks/useAuth'

const defaultEvent: Partial<Event> = {
    title: '',
    event_date: new Date().toISOString().split('T')[0],
    start_time: '12:00:00',
    description: '',
    ticket_capacity: 100,
}

const defaultLocation: Partial<Location> = {
    name: '',
    address: '',
    capacity: 100,
}

const defaultUser: Partial<User & { password?: string }> = {
    username: '',
    email: '',
    role: 'visitor',
    password: '',
}

export default function AdminDashboard() {
    const { logout } = useAuth()

    // Events state
    const [events, setEvents] = useState<Event[]>([])
    const [locationNames, setLocationNames] = useState<Record<number, string>>({})
    const [organizerNames, setOrganizerNames] = useState<Record<number, string>>({})
    const [availableTickets, setAvailableTickets] = useState<Record<number, number>>({})
    const [eventSearch, setEventSearch] = useState('')
    const [selectedEvent, setSelectedEvent] = useState<Partial<Event>>()
    const [eventOpen, setEventOpen] = useState(false)

    // Locations state
    const [locations, setLocations] = useState<Location[]>([])
    const [locationSearch, setLocationSearch] = useState('')
    const [selectedLocation, setSelectedLocation] = useState<Partial<Location>>()
    const [locationOpen, setLocationOpen] = useState(false)

    // Users state
    const [users, setUsers] = useState<User[]>([])
    const [userSearch, setUserSearch] = useState('')
    const [selectedUser, setSelectedUser] = useState<Partial<User & { password?: string }>>()
    const [userOpen, setUserOpen] = useState(false)

    const [loading, setLoading] = useState(true)

    // Fetch Events
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

            const locationsData = await Promise.all(locationPromises)
            const organizers = await Promise.all(organizerPromises)

            const locMap: Record<number, string> = {}
            locationsData.forEach((l) => (locMap[l.id] = l.name))
            setLocationNames(locMap)

            const orgMap: Record<number, string> = {}
            organizers.forEach((o) => (orgMap[o.id] = o.name))
            setOrganizerNames(orgMap)

            // Fetch available ticket counts for each event
            const ticketPromises = eventsData.map((event) =>
                api.get<number>(`/tickets/event/${event.id}/available/count`)
                    .then((res) => ({ id: event.id, count: res.data }))
                    .catch(() => ({ id: event.id, count: 0 }))
            )
            const ticketCounts = await Promise.all(ticketPromises)
            const ticketMap: Record<number, number> = {}
            ticketCounts.forEach((t) => (ticketMap[t.id] = t.count))
            setAvailableTickets(ticketMap)
        } catch (error) {
            console.error('Error fetching events:', error)
        }
    }

    // Fetch Locations
    const fetchLocations = async () => {
        try {
            const { data } = await api.get<Location[]>('/locations/')
            setLocations(data)
        } catch (error) {
            console.error('Error fetching locations:', error)
        }
    }

    // Fetch Users
    const fetchUsers = async () => {
        try {
            const { data } = await api.get<User[]>('/users/')
            setUsers(data)
        } catch (error) {
            console.error('Error fetching users:', error)
        }
    }

    useEffect(() => {
        const fetchAll = async () => {
            await Promise.all([fetchEvents(), fetchLocations(), fetchUsers()])
            setLoading(false)
        }
        fetchAll()
    }, [])

    // Event handlers
    const openEventDialog = (event: Event) => {
        setSelectedEvent({ ...event })
        setEventOpen(true)
    }

    const openNewEventDialog = () => {
        setSelectedEvent({ ...defaultEvent })
        setEventOpen(true)
    }

    const handleEventSave = async () => {
        if (!selectedEvent) return
        if (!selectedEvent.location_id) {
            alert('Please select a location')
            return
        }

        // Validate capacity against location max
        const selectedLocation = locations.find(l => l.id === selectedEvent.location_id)
        if (selectedLocation && selectedEvent.ticket_capacity && selectedEvent.ticket_capacity > selectedLocation.capacity) {
            alert(`Ticket capacity cannot exceed location capacity (${selectedLocation.capacity})`)
            return
        }

        const isUpdating = selectedEvent.id !== undefined

        try {
            if (isUpdating) {
                const { id, organizer_id, ...data } = selectedEvent
                await api.put(`/events/${id}`, data)
                setEvents((prev) =>
                    prev.map((e) => (e.id === id ? { ...selectedEvent } as Event : e))
                )
            } else {
                const { organizer_id, ...eventData } = selectedEvent
                const { data: newEvent } = await api.post<Event>('/events/', eventData)
                setEvents((prev) => [newEvent, ...prev])
            }
            setEventOpen(false)
        } catch (error) {
            console.error('Failed to save event:', error)
        }
    }

    const handleEventDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this event?')) return
        try {
            await api.delete(`/events/${id}`)
            setEvents((prev) => prev.filter((e) => e.id !== id))
        } catch (error) {
            console.error('Failed to delete event:', error)
        }
    }

    // Location handlers
    const openLocationDialog = (location: Location) => {
        setSelectedLocation({ ...location })
        setLocationOpen(true)
    }

    const openNewLocationDialog = () => {
        setSelectedLocation({ ...defaultLocation })
        setLocationOpen(true)
    }

    const handleLocationSave = async () => {
        if (!selectedLocation) return
        const isUpdating = selectedLocation.id !== undefined

        try {
            if (isUpdating) {
                const { id, ...data } = selectedLocation
                await api.put(`/locations/${id}`, data)
                setLocations((prev) =>
                    prev.map((l) => (l.id === id ? { ...selectedLocation } as Location : l))
                )
            } else {
                const { data: newLocation } = await api.post<Location>('/locations/', selectedLocation)
                setLocations((prev) => [newLocation, ...prev])
            }
            setLocationOpen(false)
        } catch (error) {
            console.error('Failed to save location:', error)
        }
    }

    const handleLocationDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this location?')) return
        try {
            await api.delete(`/locations/${id}`)
            setLocations((prev) => prev.filter((l) => l.id !== id))
        } catch (error) {
            console.error('Failed to delete location:', error)
        }
    }

    // User handlers
    const openUserDialog = (user: User) => {
        setSelectedUser({ ...user })
        setUserOpen(true)
    }

    const openNewUserDialog = () => {
        setSelectedUser({ ...defaultUser })
        setUserOpen(true)
    }

    const handleUserSave = async () => {
        if (!selectedUser) return
        const isUpdating = selectedUser.id !== undefined

        try {
            if (isUpdating) {
                const { id, password, ...data } = selectedUser
                await api.put(`/users/update/${id}`, data)
                setUsers((prev) =>
                    prev.map((u) => (u.id === id ? { ...selectedUser } as User : u))
                )
            } else {
                const { data: newUser } = await api.post<User>('/users/register', selectedUser)
                setUsers((prev) => [newUser, ...prev])
            }
            setUserOpen(false)
        } catch (error) {
            console.error('Failed to save user:', error)
        }
    }

    // Filtered data
    const filteredEvents = events.filter((item) =>
        item.title.toLowerCase().includes(eventSearch.toLowerCase()) ||
        (item.description || '').toLowerCase().includes(eventSearch.toLowerCase()) ||
        (locationNames[item.location_id] || '').toLowerCase().includes(eventSearch.toLowerCase())
    )

    const filteredLocations = locations.filter((item) =>
        item.name.toLowerCase().includes(locationSearch.toLowerCase()) ||
        item.address.toLowerCase().includes(locationSearch.toLowerCase())
    )

    const filteredUsers = users.filter((item) =>
        item.username.toLowerCase().includes(userSearch.toLowerCase()) ||
        item.email.toLowerCase().includes(userSearch.toLowerCase()) ||
        item.role.toLowerCase().includes(userSearch.toLowerCase())
    )

    const eventCols = eventColumns(openEventDialog, handleEventDelete, availableTickets)
    const locationCols = locationColumns(openLocationDialog, handleLocationDelete)
    const userCols = userColumns(openUserDialog)

    return (
        <div className="p-6 space-y-8">
            <div className="flex justify-end items-center">
                <Button onClick={logout} variant="outline">
                    Logout
                </Button>
            </div>

            {/* Events Section */}
            <section className="space-y-4">
                <h1 className="text-2xl font-bold">Events</h1>
                <div className="flex justify-between items-center gap-4">
                    <Input
                        placeholder="Search Events..."
                        value={eventSearch}
                        onChange={(e) => setEventSearch(e.target.value)}
                        className="max-w-xl"
                    />
                    <Button onClick={openNewEventDialog}>Create New Event</Button>
                </div>
                <DataTable columns={eventCols} data={filteredEvents} onRowClick={openEventDialog} />
            </section>

            {/* Locations Section */}
            <section className="space-y-4">
                <h1 className="text-2xl font-bold">Locations</h1>
                <div className="flex justify-between items-center gap-4">
                    <Input
                        placeholder="Search Locations..."
                        value={locationSearch}
                        onChange={(e) => setLocationSearch(e.target.value)}
                        className="max-w-xl"
                    />
                    <Button onClick={openNewLocationDialog}>Create New Location</Button>
                </div>
                <DataTable columns={locationCols} data={filteredLocations} onRowClick={openLocationDialog} />
            </section>

            {/* Users Section */}
            <section className="space-y-4">
                <h1 className="text-2xl font-bold">Users</h1>
                <div className="flex justify-between items-center gap-4">
                    <Input
                        placeholder="Search Users..."
                        value={userSearch}
                        onChange={(e) => setUserSearch(e.target.value)}
                        className="max-w-xl"
                    />
                    <Button onClick={openNewUserDialog}>Create New User</Button>
                </div>
                <DataTable columns={userCols} data={filteredUsers} onRowClick={openUserDialog} />
            </section>

            {/* Event Dialog */}
            <Dialog open={eventOpen} onOpenChange={setEventOpen}>
                <DialogContent onInteractOutside={(e) => e.preventDefault()}>
                    <DialogHeader>
                        <DialogTitle>{selectedEvent?.id ? 'Edit Event' : 'Create New Event'}</DialogTitle>
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
                                    <Label>Location</Label>
                                    <select
                                        className="w-full px-3 py-2 border rounded-md"
                                        value={selectedEvent.location_id || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, location_id: parseInt(e.target.value) })
                                        }
                                    >
                                        <option value="">Select a location...</option>
                                        {locations.map((loc) => (
                                            <option key={loc.id} value={loc.id}>
                                                {loc.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <Label>Capacity</Label>
                                    <Input
                                        type="number"
                                        min="1"
                                        max={locations.find(l => l.id === selectedEvent.location_id)?.capacity || undefined}
                                        value={selectedEvent.ticket_capacity || ''}
                                        onChange={(e) =>
                                            setSelectedEvent({ ...selectedEvent, ticket_capacity: parseInt(e.target.value) })
                                        }
                                    />
                                    {selectedEvent.location_id && (
                                        <p className="text-sm text-gray-500">
                                            Max: {locations.find(l => l.id === selectedEvent.location_id)?.capacity || 'N/A'}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <DialogFooter className="mt-4">
                        <Button variant="outline" onClick={() => setEventOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleEventSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Location Dialog */}
            <Dialog open={locationOpen} onOpenChange={setLocationOpen}>
                <DialogContent onInteractOutside={(e) => e.preventDefault()}>
                    <DialogHeader>
                        <DialogTitle>{selectedLocation?.id ? 'Edit Location' : 'Create New Location'}</DialogTitle>
                    </DialogHeader>

                    {selectedLocation && (
                        <div className="space-y-4 mt-4">
                            <div className="space-y-2">
                                <Label>Name</Label>
                                <Input
                                    value={selectedLocation.name || ''}
                                    onChange={(e) =>
                                        setSelectedLocation({ ...selectedLocation, name: e.target.value })
                                    }
                                    placeholder="Location Name"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Address</Label>
                                <Input
                                    value={selectedLocation.address || ''}
                                    onChange={(e) =>
                                        setSelectedLocation({ ...selectedLocation, address: e.target.value })
                                    }
                                    placeholder="Location Address"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Capacity</Label>
                                <Input
                                    type="number"
                                    min="1"
                                    value={selectedLocation.capacity || ''}
                                    onChange={(e) =>
                                        setSelectedLocation({ ...selectedLocation, capacity: parseInt(e.target.value) })
                                    }
                                    placeholder="Location Capacity"
                                />
                            </div>
                        </div>
                    )}

                    <DialogFooter className="mt-4">
                        <Button variant="outline" onClick={() => setLocationOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleLocationSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* User Dialog */}
            <Dialog open={userOpen} onOpenChange={setUserOpen}>
                <DialogContent onInteractOutside={(e) => e.preventDefault()}>
                    <DialogHeader>
                        <DialogTitle>{selectedUser?.id ? 'Edit User' : 'Create New User'}</DialogTitle>
                    </DialogHeader>

                    {selectedUser && (
                        <div className="space-y-4 mt-4">
                            <div className="space-y-2">
                                <Label>Username</Label>
                                <Input
                                    value={selectedUser.username || ''}
                                    onChange={(e) =>
                                        setSelectedUser({ ...selectedUser, username: e.target.value })
                                    }
                                    placeholder="Username"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Email</Label>
                                <Input
                                    type="email"
                                    value={selectedUser.email || ''}
                                    onChange={(e) =>
                                        setSelectedUser({ ...selectedUser, email: e.target.value })
                                    }
                                    placeholder="Email Address"
                                />
                            </div>

                            {!selectedUser.id && (
                                <div className="space-y-2">
                                    <Label>Password</Label>
                                    <Input
                                        type="password"
                                        value={selectedUser.password || ''}
                                        onChange={(e) =>
                                            setSelectedUser({ ...selectedUser, password: e.target.value })
                                        }
                                        placeholder="Password"
                                    />
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label>Role</Label>
                                <select
                                    className="w-full px-3 py-2 border rounded-md"
                                    value={selectedUser.role || 'visitor'}
                                    onChange={(e) =>
                                        setSelectedUser({ ...selectedUser, role: e.target.value })
                                    }
                                >
                                    <option value="visitor">Visitor</option>
                                    <option value="organizer">Organizer</option>
                                    <option value="superuser">Superuser</option>
                                </select>
                            </div>
                        </div>
                    )}

                    <DialogFooter className="mt-4">
                        <Button variant="outline" onClick={() => setUserOpen(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleUserSave}>Save</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
