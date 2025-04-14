import { Input, Component, OnChanges, SimpleChanges } from '@angular/core';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';
import { AuthService } from '../services/auth.service';

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

  constructor(private authService: AuthService) {}

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
  }
  onDelete() {
    const formData: {
      name: string;
      password?: string;
      authorization?: string;
    } = this.userForm.value;
    const username = formData.name;

    if (username) {
      this.authService.deleteUser(username).subscribe();
    } else {
      console.warn('Username is missing in form data');
    }
  }
}
