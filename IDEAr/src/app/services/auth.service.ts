import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { of, tap, Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { CookieService } from 'ngx-cookie-service';

import { UserData } from '../user-data';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private token: string = 'auth_token';

  constructor(
    private http: HttpClient,
    private router: Router,
    private cookieService: CookieService,
  ) {}

  login(username: string, password: string): Observable<any> {
    return this.http
      .post<{
        token?: string;
        message?: string;
        error?: string;
      }>('http://127.0.0.1:3000/trylogin', { username, password })
      .pipe(
        tap((response) => {
          if (response.token) {
            this.setToken(response.token);
          }
        }),
      );
  }

  // ? Logout (Removes Token & Redirects)
  logout(): void {
    this.removeToken();
    this.router.navigate(['/']);
  }

  // ? Check Authentication Status
  isAuthenticated(): Observable<boolean> {
    const token = this.cookieService.get(this.token);

    return this.http
      .post<{
        output?: string;
      }>('http://127.0.0.1:3000/isLoggedIn', { token })
      .pipe(
        map((response) => response.output === 'true'), // Ensure output is properly mapped to a boolean
        catchError(() => of(false)), // Return false in case of an error
      );
  }

  // ? Set Token in Cookie (7-Day Expiry)
  setToken(token: string): void {
    this.cookieService.set(
      this.token,
      token,
      7,
      '/',
      '',
      false, //TODO: set to true for production,
      'Lax',
    );
  }

  // ? Remove Token from Cookies
  removeToken(): void {
    this.cookieService.delete(this.token, '/');
  }

  levelGetter(): Observable<number> {
    const token = this.cookieService.get(this.token);
    return this.http
      .post<{
        level: number;
      }>('http://127.0.0.1:3000/checkToken', { token })
      .pipe(
        map((response) => response?.level ?? 2), // Ensure output is properly mapped to a boolean
        catchError(() => of(2)), // Return 2 in case of an error
      );
  }
  getToken(): string {
    return this.cookieService.get(this.token);
  }
  getUsers(): Observable<UserData[]> {
    return this.http
      .get<{
        status: string;
        users: UserData[];
      }>('http://127.0.0.1:3000/getUsers')
      .pipe(map((res) => res.users));
  }
  createUser(user: UserData, password: string): Observable<any> {
    return this.http.post('http://127.0.0.1:3000/register', {
      username: user.username,
      password: password,
      level: user.level,
      token: this.getToken(),
    });
  }
  updateUser(user: UserData, password: string) {
    const body = {
      username: user.username,
      password: password,
      level: user.level,
    };

    return this.http.post<{
      username: string;
      password: string;
      level: number;
      token: string;
    }>('http://127.0.0.1:3000/updateUser', body, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });
  }
}
