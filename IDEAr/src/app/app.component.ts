import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  styleUrls: ['./app.component.css'],
  templateUrl: './app.component.html',
})
export class AppComponent {
  title = 'IDEAr';
  Name: string= '';
  Size: string= '';
  isMetric: boolean=false;
  correctPW: string= 'admin1123';
  enteredPW: string= '';
  isAdminValid: boolean= false;

  getName(event: MouseEvent){
    const buttonText = (event.target as HTMLButtonElement).id;
    this.Name = buttonText;
  }

  testList = [{name: 'Self Locking Retaining Ring', size: 'SM', ismetric: false, location: "null", count: 22, threshold: 100},
              {name: 'Flat Washer', size: '7/16', ismetric: false, location: "null", count: 2, threshold: 0}
  ]
  itemInput: { [key: string]: number } = {};
  incrementCount(item: any) {
    const value = this.itemInput[item.name] ?? 1;
    item.count += value;
  }
  decrementCount(item: any) {
    const value = this.itemInput[item.name] ?? 1;
    item.count = Math.max(0, item.count - value); // re email if this hits 0?
  }

  checkPassword(){
    this.isAdminValid = this.enteredPW === this.correctPW;
  }

 

}
