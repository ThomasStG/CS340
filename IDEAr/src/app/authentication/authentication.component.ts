import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-authentication',
  templateUrl: './authentication.component.html',
  styleUrl: './authentication.component.css',
})
export class AuthenticationComponent {
  password: string = '';
  username: string = '';
  cookieName: string = 'auth_token';

  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}
  login(event: Event): void {
    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        if (response.token) {
          console.log('loggedin');
          this.router.navigate(['/admin']);
        } else {
          console.log('login failed');
          console.error(response.error); // "Invalid credentials"
        }
      },
      error: (err) => console.error('Login request failed', err),
    });
  }
}
