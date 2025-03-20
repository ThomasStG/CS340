import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { tap, Observable, of } from 'rxjs';


@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private token: string = 'auth_token';

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post<{
      token?: string;
      message?: string;
      error?: string;
    }>('http://127.0.0.1:3000/login', {
      username: username,
      password: password,
    });
  }
  logout(): void {
    localStorage.removeItem(this.token);
    this.router.navigate(['/']);
  }
  isAuthenticated(): boolean {
    return !!localStorage.getItem(this.token);
  }
  getToken(): string | null {
    return localStorage.getItem(this.token);
  }
}
