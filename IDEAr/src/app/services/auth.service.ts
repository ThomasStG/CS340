import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { of, tap, Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { CookieService } from 'ngx-cookie-service';
import { BehaviorSubject, Subject } from 'rxjs';

import { UserData } from '../user-data';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private token: string = 'auth_token';
  private authState = new BehaviorSubject<boolean>(false);
  authState$ = this.authState.asObservable();
  private _authLevel = new BehaviorSubject<number>(3); // Default level set to 3 (or any other default)
  public authLevel$ = this._authLevel.asObservable();
  private signalSource = new Subject<any>();

  signal$ = this.signalSource.asObservable();
  sendSignal(data: any) {
    console.log(data);
    this.signalSource.next(data);
  }

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
        level?: number;
        error?: string;
      }>('http://127.0.0.1:3000/trylogin', { username, password })
      .pipe(
        tap((response) => {
          if (response.token) {
            this.setToken(response.token);
            this.sendSignal(response.token);
            this.setAuthState(true);
          }
          if (response.level) {
            this._authLevel.next(response.level);
          }
        }),
      );
  }

  // ? Logout (Removes Token & Redirects)
  logout(): void {
    this.removeToken();
    this.router.navigate(['/']);
  }
  setAuthState(state: boolean) {
    this.authState.next(state);
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
  getAuthLevel(): Observable<number> {
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
  updateUser(
    username: string,
    password: string,
    level: number,
  ): Observable<any> | undefined {
    console.log(username);
    const body = {
      username: username,
      password: password,
      level: level,
      token: this.getToken(),
    };

    if (username === 'admin') {
      console.log('Admin cannot be updated');
      return;
    }
    console.log(body);
    return this.http.post<{
      username: string;
      password: string;
      level: number;
      token: string;
    }>('http://127.0.0.1:3000/updateUser', body);
  }
  deleteUser(username: string | undefined | null) {
    if (username === 'admin') {
      return;
    }
    return this.http.post('http://127.0.0.1:3000/deleteUser', {
      username: username,
      token: this.getToken(),
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });
  }
}
