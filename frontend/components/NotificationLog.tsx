"use client";

/**
 * NotificationLog Component
 * Displays history of sent Telegram notifications with details.
 * Allows clearing history.
 */

import { NotificationLog as NotificationLogType } from '@/lib/api';
import { Bell, ExternalLink, Trash2, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface NotificationLogProps {
  notifications: NotificationLogType[];
  total: number;
  onClear: () => void;
}

export default function NotificationLog({ notifications, total, onClear }: NotificationLogProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const formatTime = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <Bell className="w-5 h-5 text-primary-600" />
          Notification History
        </h2>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {notifications.length} of {total} shown
          </span>
          {notifications.length > 0 && (
            <button
              onClick={onClear}
              className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center gap-1 px-2 py-1 rounded hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No notifications sent yet</p>
          <p className="text-sm mt-1">Notifications will appear here when competitors list higher prices</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {notifications.map((notification) => {
            const isExpanded = expandedId === notification.id;
            const { payload } = notification;
            const isPositive = payload.price_difference > 0;

            return (
              <div
                key={notification.id}
                className={`border rounded-lg overflow-hidden transition-all ${
                  isPositive ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                }`}
              >
                <button
                  onClick={() => setExpandedId(isExpanded ? null : notification.id)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-opacity-80 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`} />
                    <div className="text-left">
                      <p className="font-semibold text-gray-800 text-sm">
                        {payload.competitor_name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatTime(notification.sent_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`font-bold text-sm ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
                      {isPositive ? '+' : ''}{payload.price_difference.toFixed(2)} EGP
                    </span>
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 pt-2 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">Competitor Price:</span>
                        <p className="font-medium text-gray-800">{payload.competitor_price.toFixed(2)} EGP</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Your Price:</span>
                        <p className="font-medium text-gray-800">{payload.my_price.toFixed(2)} EGP</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Max Quantity:</span>
                        <p className="font-medium text-gray-800">{payload.max_quantity.toFixed(2)} USDT</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Payment:</span>
                        <p className="font-medium text-gray-800">{payload.payment_method}</p>
                      </div>
                    </div>
                    <a
                      href={payload.ad_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View Ad on Gate.io
                    </a>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
