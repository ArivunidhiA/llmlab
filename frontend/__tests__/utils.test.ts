import {
  formatCurrency,
  formatDate,
  formatNumber,
  getInitials,
  calculatePercentageChange,
  getColorForPercentage,
  getProgressColor,
  debounce,
} from '@/lib/utils'

describe('Utility Functions', () => {
  describe('formatCurrency', () => {
    it('formats number as USD currency', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00')
      expect(formatCurrency(1000.5)).toBe('$1,000.50')
    })

    it('handles zero', () => {
      expect(formatCurrency(0)).toBe('$0.00')
    })

    it('handles negative numbers', () => {
      expect(formatCurrency(-100)).toBe('-$100.00')
    })
  })

  describe('formatDate', () => {
    it('formats date string correctly', () => {
      const result = formatDate('2024-01-15')
      expect(result).toMatch(/Jan 15, 2024/)
    })

    it('formats Date object correctly', () => {
      const date = new Date('2024-01-15')
      const result = formatDate(date)
      expect(result).toMatch(/Jan 15, 2024/)
    })
  })

  describe('formatNumber', () => {
    it('formats number with thousand separators', () => {
      expect(formatNumber(1000)).toBe('1,000')
      expect(formatNumber(1000000)).toBe('1,000,000')
    })
  })

  describe('getInitials', () => {
    it('returns initials from name', () => {
      expect(getInitials('John Doe')).toBe('JD')
      expect(getInitials('Jane Smith')).toBe('JS')
    })

    it('handles single name', () => {
      expect(getInitials('John')).toBe('J')
    })

    it('handles multiple spaces', () => {
      expect(getInitials('John Michael Doe')).toBe('JM')
    })
  })

  describe('calculatePercentageChange', () => {
    it('calculates positive change', () => {
      expect(calculatePercentageChange(150, 100)).toBe(50)
    })

    it('calculates negative change', () => {
      expect(calculatePercentageChange(50, 100)).toBe(-50)
    })

    it('handles zero previous value', () => {
      expect(calculatePercentageChange(100, 0)).toBe(0)
    })
  })

  describe('getColorForPercentage', () => {
    it('returns green color for low percentage', () => {
      expect(getColorForPercentage(25)).toContain('green')
    })

    it('returns yellow color for medium percentage', () => {
      expect(getColorForPercentage(50)).toContain('yellow')
    })

    it('returns red color for high percentage', () => {
      expect(getColorForPercentage(85)).toContain('red')
    })
  })

  describe('getProgressColor', () => {
    it('returns green for low progress', () => {
      expect(getProgressColor(30)).toBe('bg-green-500')
    })

    it('returns yellow for medium progress', () => {
      expect(getProgressColor(60)).toBe('bg-yellow-500')
    })

    it('returns red for high progress', () => {
      expect(getProgressColor(90)).toBe('bg-red-500')
    })
  })

  describe('debounce', () => {
    it('debounces function calls', async () => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn('test')
      debouncedFn('test')
      debouncedFn('test')

      expect(mockFn).not.toHaveBeenCalled()

      await new Promise((resolve) => setTimeout(resolve, 150))
      expect(mockFn).toHaveBeenCalledTimes(1)
    })
  })
})
