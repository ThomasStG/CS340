import { Component } from '@angular/core';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent {

  passwordRequired: boolean = true;
  password: string = '';

  checkPassword() {
    if (this.password === '1123') {
      this.passwordRequired = false;
    } else {
      alert('Incorrect password');
    }
  }
}
