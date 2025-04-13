import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css',
})
export class UserManagementComponent implements OnInit {
  users: UserData[] = [];

  newUserForm = new FormGroup({
    username: new FormControl(''),
    password: new FormControl(''),
    level: new FormControl('2'),
  });

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.getUsers().subscribe((response: UserData[]) => {
      this.users = response;
    });
  }
  onSubmit() {
    const formData = this.newUserForm.value;

    if (
      formData.username &&
      formData.password &&
      formData.level !== null &&
      formData.level !== undefined
    ) {
      const data: UserData = {
        username: formData.username,
        level: Number(formData.level), // ensure it's a number
      };
      const pass = formData.password as string;
      this.authService.createUser(data, pass).subscribe();
    } else {
    }
  }
}
