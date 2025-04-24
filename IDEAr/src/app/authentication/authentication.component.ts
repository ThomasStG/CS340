import { Output, Component, EventEmitter } from '@angular/core';
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
  @Output() loginSuccess = new EventEmitter<boolean>();

  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}
  login(event: Event): void {
    this.authService.login(this.username, this.password).subscribe({
      next: (response) => {
        if (response.token) {
          setTimeout(() => this.router.navigate(['/admin']), 50);
          this.authService.setAuthState(true); // after successful login
        } else {
          console.error(response.error); // "Invalid credentials"
        }
      },
      error: (err) => console.error('Login request failed', err),
    });
  }
}
