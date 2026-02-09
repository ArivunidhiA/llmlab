/**
 * CostCard Component Tests
 */

import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import CostCard from '@/components/CostCard';

describe('CostCard', () => {
  it('renders title and amount', () => {
    render(<CostCard title="Today" amount={42.50} />);
    
    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('$42.50')).toBeInTheDocument();
  });

  it('formats currency correctly', () => {
    render(<CostCard title="Test" amount={1234.56} />);
    expect(screen.getByText('$1,234.56')).toBeInTheDocument();
  });

  it('handles zero amount', () => {
    render(<CostCard title="Empty" amount={0} />);
    expect(screen.getByText('$0.00')).toBeInTheDocument();
  });

  it('handles large amounts', () => {
    render(<CostCard title="Big" amount={999999.99} />);
    expect(screen.getByText('$999,999.99')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<CostCard title="Today" amount={50} subtitle="Current day spend" />);
    expect(screen.getByText('Current day spend')).toBeInTheDocument();
  });

  it('does not render subtitle when not provided', () => {
    render(<CostCard title="Today" amount={50} />);
    expect(screen.queryByText('Current day spend')).not.toBeInTheDocument();
  });
});
