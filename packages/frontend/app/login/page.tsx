'use client';

import { useState } from 'react';
import { useAuthStore } from '../../hooks/useAuthStore';
import { useRouter } from 'next/navigation';
import { useApi } from '../../hooks/use-api';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuthStore();
  const router = useRouter();

  const { execute: loginUser, loading, error } = useApi(
    async () => {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      formData.append('grant_type', 'password');

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/token`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      login(response.data.access_token, response.data.refresh_token);
      router.push('/');
    },
    { skip: true }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      alert('Por favor, preencha usuário e senha');
      return;
    }
    try {
      await loginUser();
    } catch (error: any) {
      console.error("Login failed:", error);
      console.error("Error response:", error?.response?.data);
      alert(`Login falhou: ${error?.response?.data?.detail || error?.message || 'Erro desconhecido'}`);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Login</CardTitle>
          <CardDescription>
            Enter your username and password to access your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="testuser"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="testpass"
                required
              />
            </div>
            {error && <p className="text-sm text-red-500">{error.message}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </CardContent>
        <CardFooter>
          <p className="text-xs text-center text-gray-500 dark:text-gray-400">
            For development, you can use:
            <br />
            <strong>Username:</strong> testuser | <strong>Password:</strong> testpass
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}