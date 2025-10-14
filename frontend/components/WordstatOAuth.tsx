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
  const [manualToken, setManualToken] = useState(currentToken || '');
  const [showManualInput, setShowManualInput] = useState(false);

  useEffect(() => {
    // Проверяем URL на наличие OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');
    
    if (code) {
      handleOAuthCallback(code);
    } else if (error) {
      setError(`OAuth ошибка: ${error}`);
    }
  }, []);

  const handleOAuthCallback = async (code: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/oauth/yandex/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('✅ Токен успешно получен и сохранен!');
        setHasToken(true);
        onTokenReceived(data.access_token);
        
        // Очищаем URL от параметров
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        setError(data.error || 'Ошибка получения токена');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  const startOAuthFlow = () => {
    if (!clientId || !clientSecret) {
      setError('❌ Сначала настройте Client ID и Client Secret в настройках');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Создаем OAuth URL с правильным redirect_uri и scope
      const redirectUri = window.location.hostname === 'localhost' 
        ? 'http://localhost:3000/dashboard'
        : 'https://mcp-kv.ru/dashboard';
      
      const oauthUrl = `https://oauth.yandex.ru/authorize?` +
        `response_type=code&` +
        `client_id=${clientId}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `scope=wordstat`;

      // Переходим на страницу авторизации Yandex
      window.location.href = oauthUrl;
    } catch (err) {
      setError('Ошибка запуска OAuth');
      setIsLoading(false);
    }
  };

  const handleManualToken = async () => {
    if (!manualToken.trim()) {
      setError('Введите токен');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wordstat_access_token: manualToken.trim()
        }),
      });

      if (response.ok) {
        setSuccess('✅ Токен сохранен вручную!');
        onTokenReceived(manualToken.trim());
        setManualToken('');
        setShowManualInput(false);
      } else {
        const data = await response.json();
        setError(data.error || 'Ошибка сохранения токена');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    } finally {
      setIsLoading(false);
    }
  };

  const testToken = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/wordstat/user-info');
      const data = await response.json();

      if (response.ok) {
        setSuccess(`✅ Токен работает! Пользователь: ${data.real_name || 'Неизвестно'}`);
      } else {
        setError(data.error || 'Токен недействителен');
      }
    } catch (err) {
      setError('Ошибка проверки токена');
    } finally {
      setIsLoading(false);
    }
  };

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

      <div className="space-y-4">
        {/* Автоматическая авторизация */}
        <div>
          <h4 className="font-medium mb-2">🚀 Автоматическая авторизация</h4>
          <p className="text-sm text-gray-600 mb-3">
            Получите токен автоматически через OAuth Yandex
          </p>
          <button
            onClick={startOAuthFlow}
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {isLoading ? '⏳ Получение токена...' : '🔑 Получить токен автоматически'}
          </button>
        </div>

        {/* Ручной ввод токена */}
        <div>
          <h4 className="font-medium mb-2">✏️ Ручной ввод токена</h4>
          {!showManualInput ? (
            <button
              onClick={() => setShowManualInput(true)}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              📝 Ввести токен вручную
            </button>
          ) : (
            <div className="space-y-3">
              <textarea
                value={manualToken}
                onChange={(e) => setManualToken(e.target.value)}
                placeholder="Вставьте ваш access_token здесь..."
                className="w-full p-3 border border-gray-300 rounded-md resize-none"
                rows={3}
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleManualToken}
                  disabled={isLoading}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {isLoading ? '⏳ Сохранение...' : '💾 Сохранить токен'}
                </button>
                <button
                  onClick={() => {
                    setShowManualInput(false);
                    setManualToken('');
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
          <li>1. Убедитесь что Client ID и Client Secret настроены</li>
          <li>2. Нажмите "Получить токен автоматически"</li>
          <li>3. Разрешите доступ в окне Yandex</li>
          <li>4. Токен автоматически сохранится</li>
        </ol>
      </div>
    </div>
  );
}
