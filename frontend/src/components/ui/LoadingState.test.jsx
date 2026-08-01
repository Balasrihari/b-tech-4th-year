import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LoadingState from './LoadingState'

describe('LoadingState Component', () => {
  it('renders loading message', () => {
    render(<LoadingState message="Loading data..." />)
    expect(screen.getByText('Loading data...')).toBeInTheDocument()
  })

  it('renders default message when none provided', () => {
    render(<LoadingState />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders spinner icon', () => {
    const { container } = render(<LoadingState />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('applies correct size class', () => {
    const { container } = render(<LoadingState size="large" />)
    expect(container.firstChild).toHaveClass('text-4xl')
  })
})
