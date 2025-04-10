import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogFilePageComponent } from './log-file-page.component';

describe('LogFilePageComponent', () => {
  let component: LogFilePageComponent;
  let fixture: ComponentFixture<LogFilePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogFilePageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogFilePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
