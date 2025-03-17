import { Component } from '@angular/core';
import * as crypto from 'crypto';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'IDEAr';
  salt: string = '';
  password: string = '';

  constructor() {
    this.salt = crypto.randomBytes(16).toString('hex');
    this.password = 'password';
  }

  hashPassword(password: string): string {
    const hash = crypto
      .createHmac('sha256', this.salt)
      .update(password)
      .digest('hex');
    return hash;
  }

  checkPassword(password: string, hash: string): boolean {
    const newHash = this.hashPassword(password);
    return newHash === hash;
  }
}
