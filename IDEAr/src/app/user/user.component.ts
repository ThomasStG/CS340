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
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';

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
    public dialog: MatDialog,
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['user'] && this.user) {
      this.userForm.patchValue({
        name: this.user.username,
        authorization: String(this.user.level),
      });
    }
     /*
     *  ???
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
  }

  onUpdate() {
    const formData = this.userForm.value;
    const username = formData.name;
    const password = formData.password;
    const level = Number(formData.authorization);
    console.log(level);
    if (typeof username === 'string' && typeof password === 'string') {
      console.log(username, password, level);
      const user: UserData = { username: username, level: level };
      const result = this.authService.updateUser(username, password, level);

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
     /*
     * sets values on update
     *
     * Args:
     *   None
     *
     * Returns:
     *   updated user / error messages
     */
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
     /*
     * updates for deleting user and deisplaying new user list
     *
     * Args:
     *   None
     *
     * Returns:
     *   error or updated user list
     */
  }

  confirmPopup(value: string, warning: boolean) {
    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value, warning);
    });

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'updateUser') {
        this.onUpdate();
      }
      if (result === true && value === 'deleteUser') {
        this.onDelete();
      }
    });
     /*
     * Confirmations for updating or deleting users
     *
     * Args:
     *   string and waring boolean
     *
     * Returns:
     *   updated user list
     */
  }
}
