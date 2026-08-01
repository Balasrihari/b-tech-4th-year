import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ErrorState from './ErrorState'

describe('ErrorState Component', () => {
  it('renders error message', () => {
    render(<ErrorState message="Something went wrong" />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders default message when none provided', () => {
    render(<ErrorState />)
    expect(screen.getByText('An error occurred')).toBeInTheDocument()
  })

  it('renders retry button', () => {
    const onRetry = vi.fn()
    render(<ErrorState onRetry={onRetry} />)
    expect(screen.getByText('Try Again')).toBeInTheDocument()
  })

  it('calls onRetry when button clicked', () => {
    const onRetry = vi.fn()
    render(<ErrorState onRetry={onRetry} />)
    fireEvent.click(screen.getByText('Try Again'))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('does not render retry button when onRetry not provided', () => {
    render(<ErrorState />)
    expect(screen.queryByText('Try Again')).not.toBeInTheDocument()
  })
})
