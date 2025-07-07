import React, { useState, useEffect } from 'react';
import { get, post, patch } from '../../utils/api';

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  data: any;
  read: boolean;
  created_at: string;
}

interface NotificationPreference {
  email_enabled: boolean;
  push_enabled: boolean;
  notification_types: {
    [key: string]: string;
  };
  preferred_time: string;
  timezone: string;
}

const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchNotifications();
    fetchPreferences();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await get('/notifications/');
      setNotifications(response.data);
      setError(null);
    } catch (err) {
      setError('Error loading notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await get('/notification-preferences/');
      setPreferences(response.data);
    } catch (err) {
      console.error('Error loading notification preferences:', err);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await post(`/notifications/${notificationId}/mark_as_read/`);
      setNotifications(notifications.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      ));
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await post('/notifications/mark_all_as_read/');
      setNotifications(notifications.map(notification => ({ ...notification, read: true })));
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const updatePreferences = async (newPreferences: Partial<NotificationPreference>) => {
    try {
      const response = await patch('/notification-preferences/', newPreferences);
      setPreferences(response.data);
    } catch (err) {
      console.error('Error updating notification preferences:', err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'DAILY_REMINDER':
        return '⏰';
      case 'WORD_OF_DAY':
        return '📚';
      case 'PROGRESS_UPDATE':
        return '📈';
      case 'STREAK_ALERT':
        return '🔥';
      case 'ACHIEVEMENT':
        return '🏆';
      case 'RECOMMENDATION':
        return '🎯';
      default:
        return '📢';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Notifications</h2>
          <div className="space-x-2">
            <button
              onClick={markAllAsRead}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Mark All as Read
            </button>
            <button
              onClick={() => fetchNotifications()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        {preferences && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Notification Settings</h3>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={preferences.email_enabled}
                  onChange={(e) => updatePreferences({ email_enabled: e.target.checked })}
                  className="form-checkbox"
                />
                <span>Email Notifications</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={preferences.push_enabled}
                  onChange={(e) => updatePreferences({ push_enabled: e.target.checked })}
                  className="form-checkbox"
                />
                <span>Push Notifications</span>
              </label>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-4">Loading notifications...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-600">{error}</div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No notifications yet. They will appear here when you receive them!
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-4 rounded-lg ${
                  notification.read ? 'bg-gray-50' : 'bg-blue-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">
                      {getNotificationIcon(notification.type)}
                    </span>
                    <div>
                      <h3 className="font-semibold text-gray-800">{notification.title}</h3>
                      <p className="text-gray-600">{notification.message}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {new Date(notification.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  {!notification.read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Mark as Read
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationCenter; 