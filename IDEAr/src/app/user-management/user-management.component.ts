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
      this.authService.createUser(data, pass).subscribe({
        next: () => {
          // After creating the user, fetch the updated list of users
          this.authService.getUsers().subscribe((response: UserData[]) => {
            this.users = response; // Update users array with the new data
          });
        },
        error: (error) => {
          // Handle the error if the user creation fails
          console.error('User creation failed:', error);
        },
      });

      // Reset the form after submitting
      this.newUserForm.reset();
    } else {
    }
  }
  onUserListUpdated(updatedUsers: UserData[]) {
    this.users = updatedUsers;
  }
}
