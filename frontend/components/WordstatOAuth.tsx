'use client';

import { useState, useEffect } from 'react';

interface WordstatOAuthProps {
  clientId: string;
  clientSecret: string;
  currentToken?: string;
  onTokenReceived: (token: string) => void;
}

export default function WordstatOAuth({ 
  clientId, 
  clientSecret, 
  currentToken,
  onTokenReceived 
}: WordstatOAuthProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [authCode, setAuthCode] = useState('');
  const [showCodeInput, setShowCodeInput] = useState(false);
  const [authUrl, setAuthUrl] = useState('');

  useEffect(() => {
    // Генерируем ссылку для авторизации
    if (clientId) {
      const redirectUri = window.location.hostname === 'localhost' 
        ? 'http://localhost:3000/dashboard'
        : 'https://mcp-kv.ru/dashboard';
      
      const params = new URLSearchParams({
        client_id: clientId,
        redirect_uri: redirectUri,
        response_type: 'code'
      });
      
      setAuthUrl(`https://oauth.yandex.ru/authorize?${params.toString()}`);
    }
  }, [clientId]);

  const copyAuthUrl = () => {
    navigator.clipboard.writeText(authUrl);
    setSuccess('✅ Ссылка скопирована в буфер обмена!');
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleCodeSubmit = async () => {
    if (!authCode.trim()) {
      setError('Введите код авторизации');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/oauth/yandex/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: authCode }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('✅ Токен успешно получен и сохранен!');
        onTokenReceived(data.access_token);
        setAuthCode('');
        setShowCodeInput(false);
      } else {
        setError(data.error || 'Ошибка получения токена');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  if (!clientId || !clientSecret) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Настройка Wordstat</h3>
        <p className="text-yellow-700">
          Сначала настройте Client ID и Client Secret в разделе "Настройки"
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">🔐 Авторизация Wordstat</h3>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      <div className="space-y-6">
        {/* Шаг 1: Ссылка для авторизации */}
        <div>
          <h4 className="font-medium mb-3">📋 Шаг 1: Получите код авторизации</h4>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-3">
              Скопируйте ссылку ниже и откройте её в новой вкладке для авторизации в Yandex:
            </p>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={authUrl}
                readOnly
                className="flex-1 p-2 border border-gray-300 rounded text-sm font-mono bg-white"
              />
              <button
                onClick={copyAuthUrl}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium"
              >
                📋 Скопировать
              </button>
            </div>
          </div>
        </div>

        {/* Шаг 2: Ввод кода */}
        <div>
          <h4 className="font-medium mb-3">🔑 Шаг 2: Введите код авторизации</h4>
          {!showCodeInput ? (
            <button
              onClick={() => setShowCodeInput(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              📝 Ввести код авторизации
            </button>
          ) : (
            <div className="space-y-3">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800 mb-2">
                  После авторизации в Yandex вы будете перенаправлены на страницу с кодом в URL.
                  Скопируйте код из адресной строки (параметр <code>code=</code>) и вставьте его ниже:
                </p>
                <p className="text-xs text-blue-600">
                  Пример: <code>http://localhost:3000/dashboard?code=ABC123</code> → код: <code>ABC123</code>
                </p>
              </div>
              <input
                type="text"
                value={authCode}
                onChange={(e) => setAuthCode(e.target.value)}
                placeholder="Вставьте код авторизации здесь..."
                className="w-full p-3 border border-gray-300 rounded-md text-sm"
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleCodeSubmit}
                  disabled={isLoading}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {isLoading ? '⏳ Получение токена...' : '✅ Получить токен'}
                </button>
                <button
                  onClick={() => {
                    setShowCodeInput(false);
                    setAuthCode('');
                  }}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  ❌ Отмена
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-md">
        <h4 className="font-medium text-blue-900 mb-2">ℹ️ Инструкция:</h4>
        <ol className="text-sm text-blue-800 space-y-1">
          <li>1. Нажмите "Скопировать" и откройте ссылку в новой вкладке</li>
          <li>2. Авторизуйтесь в Yandex и разрешите доступ приложению</li>
          <li>3. Скопируйте код из адресной строки (параметр code=)</li>
          <li>4. Вставьте код в форму выше и нажмите "Получить токен"</li>
        </ol>
      </div>
    </div>
  );
}