"use client";

/**
 * SettingsForm Component
 * Provides input fields for trader name, quantity, Telegram credentials,
 * and polling interval. Includes Save/Update and Test Telegram buttons.
 */

import { useState, useEffect } from 'react';
import { api, MonitorSettings } from '@/lib/api';
import { Save, Send, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface SettingsFormProps {
  onSettingsSaved: (settings: MonitorSettings) => void;
  currentSettings?: MonitorSettings | null;
}

export default function SettingsForm({ onSettingsSaved, currentSettings }: SettingsFormProps) {
  const [settings, setSettings] = useState<MonitorSettings>({
    trader_name: '',
    min_quantity: 100,
    telegram_bot_token: '',
    telegram_chat_id: '',
    polling_interval: 10,
    payment_method: 'Instapay',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load current settings when provided
  useEffect(() => {
    if (currentSettings) {
      setSettings(currentSettings);
    }
  }, [currentSettings]);

  const handleChange = (field: keyof MonitorSettings, value: string | number) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setMessage(null);
  };

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);

    try {
      const result = await api.updateSettings(settings);
      if (result.success) {
        setMessage({ type: 'success', text: result.message });
        onSettingsSaved(settings);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to save settings' });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Network error' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    setIsTesting(true);
    setMessage(null);

    try {
      const result = await api.testTelegram(settings);
      if (result.success) {
        setMessage({ type: 'success', text: 'Test message sent! Check your Telegram.' });
      } else {
        setMessage({ type: 'error', text: 'Failed to send test message' });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to test Telegram' });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Save className="w-5 h-5 text-primary-600" />
        Monitor Settings
      </h2>

      {message && (
        <div className={`mb-4 p-3 rounded-md flex items-center gap-2 ${
          message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {message.text}
        </div>
      )}

      <div className="space-y-4">
        {/* Trader Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Your Gate.io Trader Name
          </label>
          <input
            type="text"
            value={settings.trader_name}
            onChange={(e) => handleChange('trader_name', e.target.value)}
            placeholder="e.g., CryptoTrader_EGY"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">Exact name as shown on Gate.io P2P</p>
        </div>

        {/* Minimum Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Minimum Quantity to Monitor (USDT)
          </label>
          <input
            type="number"
            value={settings.min_quantity}
            onChange={(e) => handleChange('min_quantity', parseFloat(e.target.value) || 0)}
            min={1}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">Only alert on competitors with max quantity ≥ this value</p>
        </div>

        {/* Polling Interval */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Polling Interval (seconds)
          </label>
          <input
            type="number"
            value={settings.polling_interval}
            onChange={(e) => handleChange('polling_interval', parseInt(e.target.value) || 5)}
            min={5}
            max={300}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">How often to check prices (min: 5s, recommended: 10s)</p>
        </div>

        {/* Payment Method */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Payment Method
          </label>
          <select
            value={settings.payment_method}
            onChange={(e) => handleChange('payment_method', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="Instapay">Instapay</option>
            <option value="Vodafone Cash">Vodafone Cash</option>
            <option value="Bank Transfer">Bank Transfer</option>
          </select>
        </div>

        {/* Telegram Bot Token */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Telegram Bot Token
          </label>
          <input
            type="password"
            value={settings.telegram_bot_token}
            onChange={(e) => handleChange('telegram_bot_token', e.target.value)}
            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">Get from @BotFather on Telegram</p>
        </div>

        {/* Telegram Chat ID */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Telegram Chat ID
          </label>
          <input
            type="text"
            value={settings.telegram_chat_id}
            onChange={(e) => handleChange('telegram_chat_id', e.target.value)}
            placeholder="e.g., 123456789 or -1001234567890"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500 mt-1">Your personal Chat ID or Group Chat ID</p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {isSaving ? 'Saving...' : 'Save / Update'}
          </button>

          <button
            onClick={handleTestTelegram}
            disabled={isTesting || !settings.telegram_bot_token || !settings.telegram_chat_id}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 border border-gray-300"
          >
            {isTesting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            {isTesting ? 'Testing...' : 'Test Telegram'}
          </button>
        </div>
      </div>
    </div>
  );
}
