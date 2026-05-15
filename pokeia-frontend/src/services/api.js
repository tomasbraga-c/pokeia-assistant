const BASE_URL = 'http://localhost:8000'

export async function sugerirTime(dados) {
  const resposta = await fetch(`${BASE_URL}/sugerir-time`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  })
  return resposta.json()
}

export async function compararTimes(dados) {
  const resposta = await fetch(`${BASE_URL}/comparar-times`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  })
  return resposta.json()
}

export async function chat(dados) {
    const resposta = await fetch(`${BASE_URL}/chat`, {
        method:'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    return resposta.json()
    
}

export async function analisarTime(dados) {
  const resposta = await fetch(`${BASE_URL}/analisar-time`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  })
  return resposta.json()
}