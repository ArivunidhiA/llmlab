import { render, screen } from '@testing-library/react'
import { Card, CardBody, CardHeader } from '@/components/Card'

describe('Card Components', () => {
  it('renders card with children', () => {
    render(
      <Card>
        <CardBody>Card content</CardBody>
      </Card>
    )
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders with default variant styles', () => {
    const { container } = render(
      <Card>
        <CardBody>Test</CardBody>
      </Card>
    )
    const card = container.querySelector('div')
    expect(card).toHaveClass('rounded-lg', 'border', 'bg-white')
  })

  it('renders with elevated variant', () => {
    const { container } = render(
      <Card variant="elevated">
        <CardBody>Elevated</CardBody>
      </Card>
    )
    const card = container.querySelector('div')
    expect(card).toHaveClass('shadow-md')
  })

  it('renders CardHeader with title', () => {
    render(<CardHeader title="Test Title" />)
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('renders CardHeader with subtitle', () => {
    render(<CardHeader title="Title" subtitle="Subtitle" />)
    expect(screen.getByText('Subtitle')).toBeInTheDocument()
  })

  it('renders CardBody with children', () => {
    render(<CardBody>Body content</CardBody>)
    expect(screen.getByText('Body content')).toBeInTheDocument()
  })
})
