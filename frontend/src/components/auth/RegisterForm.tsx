import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  target_language: string;
  current_level: string;
  learning_goal: string;
  daily_goal_minutes: number;
}

const RegisterForm: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    target_language: 'EN',
    current_level: 'A1',
    learning_goal: 'CASUAL',
    daily_goal_minutes: 15,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/users/register/', formData);
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      navigate('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                name="username"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
              />
            </div>
            <div>
              <input
                name="email"
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <input
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="target_language" className="block text-sm font-medium text-gray-700">
                Target Language
              </label>
              <select
                name="target_language"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={formData.target_language}
                onChange={handleChange}
              >
                <option value="EN">English</option>
                <option value="ES">Spanish</option>
                <option value="FR">French</option>
                <option value="DE">German</option>
                <option value="IT">Italian</option>
                <option value="PT">Portuguese</option>
                <option value="RU">Russian</option>
                <option value="ZH">Chinese</option>
                <option value="JA">Japanese</option>
                <option value="KO">Korean</option>
              </select>
            </div>

            <div>
              <label htmlFor="current_level" className="block text-sm font-medium text-gray-700">
                Current Level
              </label>
              <select
                name="current_level"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={formData.current_level}
                onChange={handleChange}
              >
                <option value="A1">Beginner</option>
                <option value="A2">Elementary</option>
                <option value="B1">Intermediate</option>
                <option value="B2">Upper Intermediate</option>
                <option value="C1">Advanced</option>
                <option value="C2">Mastery</option>
              </select>
            </div>

            <div>
              <label htmlFor="learning_goal" className="block text-sm font-medium text-gray-700">
                Learning Goal
              </label>
              <select
                name="learning_goal"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={formData.learning_goal}
                onChange={handleChange}
              >
                <option value="CASUAL">Casual Learning</option>
                <option value="TRAVEL">Travel</option>
                <option value="BUSINESS">Business</option>
                <option value="ACADEMIC">Academic</option>
                <option value="FLUENCY">Native-like Fluency</option>
              </select>
            </div>

            <div>
              <label htmlFor="daily_goal_minutes" className="block text-sm font-medium text-gray-700">
                Daily Goal (minutes)
              </label>
              <input
                type="number"
                name="daily_goal_minutes"
                min="5"
                max="120"
                step="5"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                value={formData.daily_goal_minutes}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterForm; 