import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Trash2 } from "lucide-react"

export interface Event {
  id: number
  title: string
  event_date: string
  start_time: string
  description?: string
  ticket_capacity: number
  location_id: number
  organizer_id: number
}

interface Column<T> {
  header: string
  accessorKey?: keyof T
  cell?: (item: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  onRowClick: (item: T) => void
}

export function DataTable<T extends { id: number }>({ columns, data, onRowClick }: DataTableProps<T>) {
  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 shadow-sm">
      <Table>
        <TableHeader className="bg-gray-100">
          <TableRow>
            {columns.map((col, i) => (
              <TableHead key={i} className="text-gray-700">
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={columns.length} className="text-center py-4 text-gray-500">
                No results found.
              </TableCell>
            </TableRow>
          ) : (
            data.map((item, index) => (
              <TableRow
                key={item.id}
                className={index % 2 === 0 ? "bg-white cursor-pointer hover:bg-gray-50 transition-colors" : "bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"}
                onClick={() => onRowClick(item)}
              >
                {columns.map((col, i) => (
                  <TableCell key={i}>
                    {col.cell ? col.cell(item) : col.accessorKey ? (item[col.accessorKey] as any) : null}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

export const eventColumns = (onEdit: (e: Event) => void, onDelete: (id: number) => void) => [
  { header: "Title", accessorKey: "title" as const },
  { header: "Date", accessorKey: "event_date" as const },
  { header: "Time", accessorKey: "start_time" as const },
  {
    header: "Actions",
    cell: (event: Event) => (
      <Button
        variant="ghost"
        size="icon"
        onClick={(e) => {
          e.stopPropagation()
          onDelete(event.id)
        }}
      >
        <Trash2 className="h-4 w-4 text-red-500" />
      </Button>
    ),
  },
]
