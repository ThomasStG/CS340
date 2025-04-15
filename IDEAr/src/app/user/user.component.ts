import { Input, Component, OnChanges, SimpleChanges } from '@angular/core';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';


@Component({
  selector: 'app-user',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css'], // Corrected here
})
export class UserComponent implements OnChanges {
  @Input() user: UserData = { username: '', level: 2 };

  userForm = new FormGroup({
    name: new FormControl(''),
    password: new FormControl(''),
    authorization: new FormControl('2'),
  });

  constructor(
    private authService: AuthService,
    public dialog: MatDialog,

  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['user'] && this.user) {
      this.userForm.patchValue({
        name: this.user.username,
        authorization: String(this.user.level),
      });
    }
  }

  onUpdate() {
    const formData = this.userForm.value;
  }
  onDelete() {
  }


  confirmPopup(value: string) {
      const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
      ConfirmationPopUp.afterOpened().subscribe(() => {
        ConfirmationPopUp.componentInstance.updatePopup(value);
      });
  
      ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
        if (result === true && value === 'update') {
          this.onUpdate();
        }
        if (result === true && value === 'delete') {
          this.onDelete();
        }
      });
    }
}
