import {
  Output,
  Input,
  Component,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { EventEmitter } from '@angular/core';

@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css'], // Corrected here
})
export class UserComponent implements OnChanges {
  @Input() user: UserData = { username: '', level: 2 };
  @Output() userListUpdated = new EventEmitter<UserData[]>();

  userForm = new FormGroup({
    name: new FormControl(''),
    password: new FormControl(''),
    authorization: new FormControl('2'),
  });
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['user'] && this.user) {
      this.userForm.patchValue({
        name: this.user.username,
        authorization: String(this.user.level),
      });
    }
  }

  onSubmit() {
    const formData = this.userForm.value;
    const username = formData.name;
    const password = formData.password;
    const level = Number(formData.authorization);
    if (
      typeof username === 'string' &&
      username.trim() !== '' &&
      typeof password === 'string' &&
      password.trim() !== '' &&
      typeof level === 'number'
    ) {
      const user = { username, level };
      const result = this.authService.updateUser(user, password);

      if (result) {
        result.subscribe({
          // safe: only called if defined
          next: () => {
            // Fetch the updated user list after deleting the user
            this.authService
              .getUsers()
              .subscribe((updatedUsers: UserData[]) => {
                this.userListUpdated.emit(updatedUsers); // Emit updated list to the parent
              });
          },
          error: (err) => {
            console.error('Error deleting user:', err);
          },
        });
      } else {
        console.warn('Delete request was skipped (maybe admin user)');
      }
    } else {
      console.warn('Invalid or missing username');
    }
  }

  // onDelete() {
  //   const formData = this.userForm.value;
  //   const username = formData.name;
  //   this.authService.deleteUser(username).subscribe({
  //     next: () => {
  //       // Fetch the updated user list after deleting the user
  //       this.authService.getUsers().subscribe((updatedUsers: UserData[]) => {
  //         this.userListUpdated.emit(updatedUsers); // Emit updated list to the parent
  //       });
  //     },
  //     error: (err) => {
  //       console.error('Error deleting user:', err);
  //     },
  //   });
  // }
  onDelete() {
    const username = this.userForm.get('name')?.value;

    if (typeof username === 'string' && username.trim() !== '') {
      const result = this.authService.deleteUser(username);

      if (result) {
        result.subscribe({
          // safe: only called if defined
          next: () => {
            // Fetch the updated user list after deleting the user
            this.authService
              .getUsers()
              .subscribe((updatedUsers: UserData[]) => {
                this.userListUpdated.emit(updatedUsers); // Emit updated list to the parent
              });
          },
          error: (err) => {
            console.error('Error deleting user:', err);
          },
        });
      } else {
        console.warn('Delete request was skipped (maybe admin user)');
      }
    } else {
      console.warn('Invalid or missing username');
    }
  }
}
