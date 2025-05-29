import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataDownloadElectricalComponent } from './data-download-electrical.component';

describe('DataDownloadElectricalComponent', () => {
  let component: DataDownloadElectricalComponent;
  let fixture: ComponentFixture<DataDownloadElectricalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DataDownloadElectricalComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DataDownloadElectricalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
