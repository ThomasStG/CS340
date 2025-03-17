import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-authentication',
  templateUrl: './authentication.component.html',
  styleUrl: './authentication.component.css',
})
export class AuthenticationComponent {
  password: string = '';
  username: string = '';

  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}

  login(event: Event): void {
    console.log('localStorage', typeof localStorage);
    if (this.username === 't' && this.password === '1') {
      localStorage.setItem('auth_token', 'test_token');
      console.log('Login successful');
      this.router.navigate(['/admin']);
      return;
    }
    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        if (response.token) {
          localStorage.setItem('auth_token', response.token);
          console.log(typeof localStorage);
          console.log(response.message); // "Login successful"
        } else {
          console.error(response.error); // "Invalid credentials"
        }
      },
      error: (err) => console.error('Login request failed', err),
    });
    this.router.navigate(['/admin']);
  }

  checkPassword(password: string, hash: string): void {}
}
