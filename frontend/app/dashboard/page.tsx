'use client'

import { useEffect, useState } from 'react'
import api from '@/app/api'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

import ProtectedRoute from '../protectedRoute'


import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

import { Button } from '@/components/ui/button'


interface Event {
  id: number
  title: string
  event_date: string
  start_time: string
  description?: string
  ticket_capacity: number
  location_id: number
  organizer_id: number
}

export default function DashboardPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [locationNames, setLocationNames] = useState<Record<number, string>>({})
  const [organizerNames, setOrganizerNames] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)

  const [selectedEvent, setSelectedEvent] = useState<Event>();
  const [open, setOpen] = useState(false);

  const openDialog = (event: Event) => {
    setSelectedEvent({ ...event });
    setOpen(true);
  };

  const handleSave = () => {
    if (!selectedEvent) return;
    setEvents((prev) =>
      prev.map((e) => (e.id === selectedEvent.id ? selectedEvent : e))
    );
    setOpen(false);
  };





  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const { data: eventsData } = await api.get<Event[]>('/events/')
        setEvents(eventsData)

        // Extract unique IDs
        const locationIds = Array.from(new Set(eventsData.map((e) => e.location_id)))
        const organizerIds = Array.from(new Set(eventsData.map((e) => e.organizer_id)))

        // Fetch details
        const locationPromises = locationIds.map((id) =>
          api.get(`/locations/${id}`).then((res) => ({ id, name: res.data.name }))
        )
        const organizerPromises = organizerIds.map((id) =>
          api.get(`/users/${id}`).then((res) => ({ id, name: res.data.username }))
        )

        const locations = await Promise.all(locationPromises)
        const organizers = await Promise.all(organizerPromises)

        // Create lookup maps
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

    fetchEvents()
  }, [])


  return (
    <ProtectedRoute>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold">Events Dashboard</h1>

        <div className="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
          <Table>
            <TableHeader className="bg-gray-100">
              <TableRow>
                <TableHead className="text-gray-700">Title</TableHead>
                <TableHead className="text-gray-700">Event Date</TableHead>
                <TableHead className="text-gray-700">Start Time</TableHead>
                <TableHead className="text-gray-700">Location</TableHead>
                <TableHead className="text-gray-700">Organizer</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {events.map((event, index) => (
                  <TableRow
                  key={event.id}
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50 cursor-pointer'}
                  onClick={() => openDialog(event)}
                  >
                  <TableCell>{event.title}</TableCell>
                  <TableCell>{event.event_date}</TableCell>
                  <TableCell>{event.start_time}</TableCell>
                  <TableCell>{locationNames[event.location_id] || event.location_id}</TableCell>
                  <TableCell>{organizerNames[event.organizer_id] || event.organizer_id}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Event</DialogTitle>
            </DialogHeader>
            {selectedEvent && (
              <div className="space-y-4 mt-4">
                <Input
                  value={selectedEvent.title}
                  onChange={(e) =>
                    setSelectedEvent({ ...selectedEvent, title: e.target.value })
                  }
                  placeholder="Event Title"
                />
                <Input
                  value={selectedEvent.description || ''}
                  onChange={(e) =>
                    setSelectedEvent({ ...selectedEvent, description: e.target.value })
                  }
                  placeholder="Description"
                />
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
    </ProtectedRoute>
  )
}
