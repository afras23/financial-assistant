import React, { useEffect, useState } from 'react'
import { api } from './api'

type Expense = {
  id: string
  user_id: string
  amount: number
  currency: string
  description: string
  merchant?: string | null
  category?: string | null
}

export default function App() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [summary, setSummary] = useState<any>(null)

  // form state
  const [amount, setAmount] = useState<string>("")
  const [currency, setCurrency] = useState<string>("GBP")
  const [description, setDescription] = useState<string>("")

  // demo user id for now
  const userId = '00000000-0000-0000-0000-000000000001'

  const refresh = async () => {
    const [e, s] = await Promise.all([
      api.get('/expenses'),
      api.get('/insights/summary', { params: { user_id: userId } })
    ])
    setExpenses(e.data)
    setSummary(s.data)
  }

  const addExpense = async () => {
    if (!amount || !description) return alert("Enter amount and description")
    const idempotency_key = `web-${Date.now()}-${Math.random().toString(16).slice(2)}`
    await api.post('/expenses', {
      user_id: userId,
      amount: parseFloat(amount),
      currency,
      description,
      idempotency_key
    })
    setAmount("")
    setDescription("")
    await refresh()
  }

  useEffect(() => { refresh() }, [])

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 24, maxWidth: 960, margin: '0 auto' }}>
      <h1>💸 Financial Assistant</h1>
      <p>ML-driven expense parsing and budgeting.</p>

      <section style={{ marginTop: 24, padding: 16, border: '1px solid #eee', borderRadius: 8 }}>
        <h2>Add Expense</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: 8, alignItems: 'center' }}>
          <input
            placeholder="Description e.g. Latte at Starbucks"
            value={description}
            onChange={e => setDescription(e.target.value)}
            style={{ padding: 8 }}
          />
          <input
            placeholder="Amount"
            type="number"
            step="0.01"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            style={{ padding: 8 }}
          />
          <input
            placeholder="Currency"
            value={currency}
            onChange={e => setCurrency(e.target.value.toUpperCase().slice(0,3))}
            style={{ padding: 8 }}
          />
          <button onClick={addExpense} style={{ padding: '8px 12px' }}>Add</button>
        </div>
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Summary (last 30 days)</h2>
        <pre>{summary ? JSON.stringify(summary, null, 2) : '—'}</pre>
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Recent Expenses</h2>
        <table width="100%" cellPadding={8} style={{ borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th align="left">Description</th>
              <th align="right">Amount</th>
              <th>Currency</th>
              <th>Merchant</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map(e => (
              <tr key={e.id} style={{ borderTop: '1px solid #ddd' }}>
                <td>{e.description}</td>
                <td align="right">{e.amount.toFixed(2)}</td>
                <td>{e.currency}</td>
                <td>{e.merchant || '—'}</td>
                <td>{e.category || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <button onClick={refresh} style={{ marginTop: 16, padding: '8px 12px' }}>Refresh</button>
    </div>
  )
}

