import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import EmptyState from './EmptyState'

describe('EmptyState Component', () => {
  it('renders title', () => {
    render(<EmptyState title="No data found" />)
    expect(screen.getByText('No data found')).toBeInTheDocument()
  })

  it('renders description', () => {
    render(<EmptyState description="There are no items to display" />)
    expect(screen.getByText('There are no items to display')).toBeInTheDocument()
  })

  it('renders action button when provided', () => {
    const onAction = vi.fn()
    render(<EmptyState actionLabel="Add Item" onAction={onAction} />)
    expect(screen.getByText('Add Item')).toBeInTheDocument()
  })

  it('calls onAction when button clicked', () => {
    const onAction = vi.fn()
    render(<EmptyState actionLabel="Add Item" onAction={onAction} />)
    fireEvent.click(screen.getByText('Add Item'))
    expect(onAction).toHaveBeenCalledTimes(1)
  })

  it('does not render action button when not provided', () => {
    render(<EmptyState />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
