import { Component } from '@angular/core';
import { AuthService } from './auth.service';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'IDEAr';

  constructor(public authService: AuthService) {}
  logout() {
    this.authService.logout();
  }
}
